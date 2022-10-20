from apiRegistry.openfood_lib import openfood
from apiRegistry.openfood_lib.openfood_env import KV1_ORG_POOL_WALLETS
openfood.connect_kv1_node()
openfood.check_kv1_wallet()
openfood.update_kv_foundation()
openfood.verify_kv_foundation()
