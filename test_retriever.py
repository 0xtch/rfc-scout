
import unittest
from retriever import retrieve, tokenize


class TestRetriever(unittest.TestCase):

    def test_normalization(self):
        self.assertEqual(
            tokenize("BGP-4, ROUTING!"),
            {"bgp", "4", "routing"}
        )

    def test_ranking(self):
        documents = [
            "BGP uses TCP.",
            "BGP exchanges routing information.",
            "OSPF is a link-state routing protocol."
        ]
        self.assertEqual(
            retrieve("BGP routing", documents, k=2),
            [documents[1], documents[0]]
        )

    def test_ties(self):
        documents = ["BGP peers", "BGP routes", "BGP updates"]
        self.assertEqual(
            retrieve("BGP", documents, k=2),
            documents[:2]
        )

    def test_empty_query(self):
        self.assertEqual(retrieve("", ["BGP"]), [])

    def test_empty_documents(self):
        self.assertEqual(retrieve("BGP", []), [])

    def test_no_matches(self):
        self.assertEqual(retrieve("OSPF", ["BGP routing"]), [])

    def test_k_exceeds_collection(self):
        documents = ["BGP peers", "BGP routes"]
        self.assertEqual(retrieve("BGP", documents, k=10), documents)

    def test_nonpositive_k(self):
        self.assertEqual(retrieve("BGP", ["BGP peers"], k=0), [])
        self.assertEqual(retrieve("BGP", ["BGP peers"], k=-1), [])


if __name__ == "__main__":
    unittest.main()
