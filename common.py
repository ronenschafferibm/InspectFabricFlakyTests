import re

gossip_modules = [
    "github.com/hyperledger/fabric/gossip/api",
    "github.com/hyperledger/fabric/gossip/comm",
    "github.com/hyperledger/fabric/gossip/comm/mock",
    "github.com/hyperledger/fabric/gossip/common",
    "github.com/hyperledger/fabric/gossip/discovery",
    "github.com/hyperledger/fabric/gossip/election",
    "github.com/hyperledger/fabric/gossip/filter",
    "github.com/hyperledger/fabric/gossip/gossip",
    "github.com/hyperledger/fabric/gossip/gossip/algo",
    "github.com/hyperledger/fabric/gossip/gossip/channel",
    "github.com/hyperledger/fabric/gossip/gossip/msgstore",
    "github.com/hyperledger/fabric/gossip/gossip/pull",
    "github.com/hyperledger/fabric/gossip/identity",
    "github.com/hyperledger/fabric/gossip/integration",
    "github.com/hyperledger/fabric/gossip/metrics",
    # "github.com/hyperledger/fabric/gossip/metrics/mocks",
    # "github.com/hyperledger/fabric/gossip/mocks",
    "github.com/hyperledger/fabric/gossip/privdata",
    # "github.com/hyperledger/fabric/gossip/privdata/common",
    # "github.com/hyperledger/fabric/gossip/privdata/mocks",
    "github.com/hyperledger/fabric/gossip/protoext",
    "github.com/hyperledger/fabric/gossip/service",
    # "github.com/hyperledger/fabric/gossip/service/mocks",
    "github.com/hyperledger/fabric/gossip/state",
    "github.com/hyperledger/fabric/gossip/state/mocks",
    "github.com/hyperledger/fabric/gossip/util",
]


def find_failed_tests(log_file):
    failed_tests = []
    with open(log_file, "r", encoding="unicode_escape") as f:
        log = f.read()
        fail_pattern = r"--- FAIL:\s+(.*?)\s"
        failed_tests = re.findall(fail_pattern, log)
        if not failed_tests:
            failed_tests = ['*** unknown test ***']
    return failed_tests