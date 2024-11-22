
# Time Complexity: O(m*N) m: number of strings n: length of the string
# Space Complexity: O(1)
import logging 
def min_deletions_remove_duplicates(strings):
    """
    calculate the minimum number of deletions needed to remove duplicates from each string

    :param strings: List[str] - list of input string 
    :return: List[int] - the minimum number of deletions needed to remove duplicates from each string
    """
    results = []
    for s in strings:
        deletions = 0
        for i in range(1, len(s)):
            if s[i] == s[i - 1]:
                deletions += 1
        results.append(deletions)
    return results

# 测试用例
def test_cases():
  test_input = ["AAAA", "BBBBB", "ABABABAB", "AAABBB"]
  expected_output = [3, 4, 0, 4]
  assert min_deletions_remove_duplicates(test_input) == expected_output
  logging.info("Test Case 1 Passed.")

  test_input = ["AAB", "AABB", "ABBA", "ABAB"]
  expected_output = [1, 2, 1, 0]
  assert min_deletions_remove_duplicates(test_input) == expected_output
  logging.info("Test case 2 Passed.")

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  test_cases()
  logging.info("All test cases passed.")