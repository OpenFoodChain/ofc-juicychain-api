from rest_framework import routers, serializers, viewsets
from django.urls import path, include
from django.core.validators import RegexValidator
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import (
    Organization,
    Certificate,
    CertificateRule,
    Location,
    Batch,
    PoolWallet,
    KV
)
#import openfood_lib.openfood
#import models
from .openfood_lib import openfood
import json

class BaseWalletSerializer(serializers.ModelSerializer):
    # TODO when using uuid
    # id = serializers.UUIDField(read_only=True)
    pubkey = serializers.CharField(
        max_length=66,
        validators=[
            RegexValidator(
                regex='^.{66}$',
                message='Incorrect pubkey length, must be 66',
                code='pubkey66')])
    raddress = serializers.CharField(
        max_length=34,
        validators=[
            RegexValidator(
                regex='^.{34}$',
                message='Incorrect raddress length, must be 34',
                code='raddress34')])

    class Meta:
        # abstract = True
        fields = ['id', 'pubkey', 'raddress']


class OrganizationSerializer(BaseWalletSerializer):

    class Meta:
        model = Organization
        fields = ['id', 'name', 'pubkey', 'raddress']


class KvSerializer(serializers.ModelSerializer):
	key = serializers.CharField(
	max_length=66 )
	keylen = serializers.CharField(
	max_length=255 )
	
	class Meta:
		model = KV
		fields = ['key', 'keylen']


class CertificateSerializer(BaseWalletSerializer):

    # rule = CertificateRuleSerializer(many=True)
    pubkey = serializers.CharField(allow_blank=True)
    raddress = serializers.CharField(allow_blank=True)

    class Meta:
        model = Certificate
        fields = ['id', 'name', 'date_issue', 'date_expiry', 'issuer', 'identifier', 'pubkey', 'raddress', 'txid_funding', 'organization']


class CertificateRuleSerializer(BaseWalletSerializer):
    # id = serializers.UUIDField(read_only=True)

    pubkey = serializers.CharField(allow_blank=True)
    raddress = serializers.CharField(allow_blank=True)

    class Meta:
        model = CertificateRule
        fields = ['id', 'name', 'condition', 'pubkey', 'raddress', 'certificate']


class LocationSerializer(BaseWalletSerializer):
    # works
    # organization = OrganizationSerializer(read_only=True)
    pubkey = serializers.CharField(allow_blank=True)
    raddress = serializers.CharField(allow_blank=True)
    
    class Meta:
        model = Location
        fields = ['id', 'name', 'pubkey', 'raddress', 'organization', 'txid_funding']


class BatchSerializer(BaseWalletSerializer):

    pubkey = serializers.CharField(allow_blank=True)
    raddress = serializers.CharField(allow_blank=True)

    class Meta:
        model = Batch
        fields = ['id', 'identifier', 'jds', 'jde', 'date_production_start', 'date_best_before', 'delivery_date', 'origin_country', 'mass_balance', 'pubkey', 'raddress', 'organization']


class PoolWalletSerializer(BaseWalletSerializer):

    class Meta:
        model = PoolWallet
        fields = ['id', 'name', 'pubkey', 'raddress', 'organization']


# Nested Serializer


class NestedBatchSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Batch
        exclude = ['url', 'organization']


class NestedCertificateRuleSerializer(serializers.HyperlinkedModelSerializer):
    # id = serializers.UUIDField(read_only=True)

    class Meta:
        model = CertificateRule
        exclude = ['url', 'certificate']


class NestedLocationSerializer(serializers.HyperlinkedModelSerializer):
    # organization = OrganizationSerializer()

    class Meta:
        model = Location
        exclude = ['url', 'organization']
        # fields = '__all__'


class NestedPoolWalletSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = PoolWallet
        exclude = ['url', 'organization']


class NestedCertificateSerializer(serializers.HyperlinkedModelSerializer):
    rule = NestedCertificateRuleSerializer(many=True)

    class Meta:
        model = Certificate
        exclude = ['url', 'organization']
        # fields = '__all__'


class NestedOrganizationSerializer(serializers.HyperlinkedModelSerializer):
    location = NestedLocationSerializer(many=True)
    certificate = NestedCertificateSerializer(many=True)
    batch = NestedBatchSerializer(many=True)
    pool_wallet = NestedPoolWalletSerializer(many=True)

    class Meta:
        model = Organization
        depth = 3
        fields = ['id', 'name', 'pubkey', 'raddress', 'pool_wallet', 'location', 'certificate', 'batch']

    def create(self, validated_data):
        organization = Organization.objects.get(name=validated_data.get('name'))

        pool_wallet_field = self.context['request'].data['pool_wallet']
        pool_wallet_data = validated_data.pop('pool_wallet')
        pool_wallet_serializer = self.fields['pool_wallet']

        for key, each in enumerate(pool_wallet_data):
            each['organization'] = organization
            each['pubkey'] = pool_wallet_field[key]['pubkey']
            each['raddress'] = pool_wallet_field[key]['raddress']

        batch_field = self.context['request'].data['batch']
        batch_data = validated_data.pop('batch')
        batch_serializer = self.fields['batch']

        for key, each in enumerate(batch_data):
            each['organization'] = organization
            each['pubkey'] = batch_field[key]['pubkey']
            each['raddress'] = batch_field[key]['raddress']

        location_data = validated_data.pop('location')
        location_serializer = self.fields['location']

        for each in location_data:
            each['organization'] = organization

        cert_field = self.context['request'].data['certificate']
        certificate_data = validated_data.pop('certificate')
        certificate_serializer = self.fields['certificate']

        for key, each in enumerate(certificate_data):
            each['organization'] = organization

            del each['rule']

        pool_wallet = pool_wallet_serializer.create(pool_wallet_data)
        batch = batch_serializer.create(batch_data)
        location = location_serializer.create(location_data)
        certificate = certificate_serializer.create(certificate_data)

        for item in cert_field:
            for items in item['rule']:
                CertificateRule.objects.create(
                    raddress=items['raddress'],
                    pubkey=items['pubkey'],
                    name=items['name'],
                    condition=items['condition'],
                    certificate=Certificate.objects.get(name=item['name'], raddress=item['raddress'], pubkey=item['pubkey'])
                )

        return organization


# Standalone ViewSet
##################################


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        queryset = Organization.objects.all()
        raddress = self.request.query_params.get('raddress', None)
        if (raddress is not None):
            queryset = queryset.filter(raddress=raddress)[0:1]
        return queryset


    def patch(self, request, *args, **kwargs):
        openfood.connect_batch_node()
        data = {"mylo": "testing123"}
        kv_response = openfood.kvupdate_wrapper("mylokv1", data, "1", "mylo")
        return Response(kv_response, status=status.HTTP_201_CREATED)


class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer

    def get_queryset(self):
        queryset = Certificate.objects.all()
        org_id = self.request.query_params.get('orgid', None)
        if (org_id is not None):
            queryset = queryset.filter(organization=org_id)
        return queryset

    @action(detail=False)  # listview
    def noraddress(self, request, pk=None):
        no_raddress = Certificate.objects.filter(
            raddress__exact=''
        )
        serializer = self.get_serializer(no_raddress, many=True)
        return Response(serializer.data)


class CertificateRuleViewSet(viewsets.ModelViewSet):
    queryset = CertificateRule.objects.all()
    serializer_class = CertificateRuleSerializer

    @action(detail=False)  # listview
    def noraddress(self, request, pk=None):
        no_raddress = CertificateRule.objects.filter(
            raddress__exact=''
        )
        serializer = self.get_serializer(no_raddress, many=True)
        return Response(serializer.data)


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    def get_queryset(self):
        queryset = Location.objects.all()
        org_id = self.request.query_params.get('orgid', None)
        if (org_id is not None):
            queryset = queryset.filter(organization=org_id)
        return queryset
    @action(detail=False)  # listview
    
    def noraddress(self, request, pk=None):
        org_id = self.request.query_params.get('orgid', None)
        if (org_id is not None):
            no_raddress = Location.objects.filter(
                raddress__exact='',
                organization=org_id
            )
        serializer = self.get_serializer(no_raddress, many=True)
        return Response(serializer.data)

# class proxyKV():
#	key = ""
#	value = ""
#
#	def __init__(self, iKey, iValue):
#		self.key = iKey
#		self.value = iValue


class KvViewSet(viewsets.ModelViewSet):
    queryset = KV.objects.none()
    serializer_class = KvSerializer	
    openfood.connect_kv1_node()

    def get_queryset(self):
        print("KV")
        key = self.request.query_params.get('key', None)
        if not key:
            key = openfood.get_this_node_raddress()
        value = openfood.kvsearch_wrapper(key + "_ORG_POOL_WALLETS")
        print(value)
        if 'value' not in value:
            return KV.objects.none()
        return value


class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    print("HERE")

    def get_queryset(self):
        print("CHCKING")
        queryset = Batch.objects.all()
        bbd = self.request.query_params.get('bbd', None)
        jds = self.request.query_params.get('jds', None)
        raddress = self.request.query_params.get('raddress', None)
        if (bbd is not None) and (jds is not None):
            # TODO find better querying techniques
            queryset = queryset.filter(date_best_before=bbd, jds=jds)[0:1]
        if (raddress is not None):
            queryset = queryset.filter(raddress=raddress)[0:1]
            
        return queryset


class PoolWalletViewSet(viewsets.ModelViewSet):
    queryset = PoolWallet.objects.all()
    serializer_class = PoolWalletSerializer


# Nested ViewSet
#################################


class NestedOrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = NestedOrganizationSerializer


router = routers.DefaultRouter()
router.register(r'api/v1/organization', OrganizationViewSet)
router.register(r'api/v1/organization-detail', NestedOrganizationViewSet, basename='organization-detail')
router.register(r'api/v1/location', LocationViewSet)
router.register(r'api/v1/certificate', CertificateViewSet)
router.register(r'api/v1/certificate-rule', CertificateRuleViewSet)
router.register(r'api/v1/batch', BatchViewSet)
router.register(r'api/v1/pool-wallet', PoolWalletViewSet)
router.register(r'api/v1/kv', KvViewSet)
# router.register(r'api/v1/organization/<str:raddress>/certificate', CertificateViewSet)
# router.register(r'api/v1/organization/(?P<id>[0-9a-f-]+)/location', LocationViewSet)
router.register(r'api/v1/organization/(?P<id>\d+)/location', LocationViewSet)
router.register(r'api/v1/organization/(?P<id>\d+)/certificate', CertificateViewSet)

# TODO works for id as integer, for UUID needs test
# router.register(r'api/v1/organization-detail/(?P<id>[0-9a-f]+)/location', LocationViewSet)
# router.register(r'api/v1/organization/(?P<raddress>[0-9a-f-]+)/location', LocationViewSet)
# router.register(r'api/v1/organization/<uuid:id>/batch', BatchViewSet)
# router.register(r'api/v1/organization/<uuid:id>/poolpo', PoolPurchaseOrderViewSet)
# router.register(r'api/v1/organization/<uuid:id>/poolbatch', PoolBatchViewSet)
# did not work
# router.register(r'api/v1/certificate-new', CertificateViewSet.as_view({'get': 'no_raddress'}), basename='certificate-new')

urlpatterns = [
    path('', include(router.urls)),
    path('api/v1/certificate-new/', CertificateViewSet.as_view({'get': 'noraddress'})),
    path('api/v1/certificate-rule-new/', CertificateRuleViewSet.as_view({'get': 'noraddress'}))
]

