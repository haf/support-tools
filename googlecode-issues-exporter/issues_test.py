# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for issues."""

# pylint: disable=missing-docstring,protected-access

import collections
import copy
import unittest

import issues


DEFAULT_USERNAME = "default_username"
REPO = "repo"

USER_MAP = collections.defaultdict(lambda: DEFAULT_USERNAME)
USER_MAP.update({
    "user@email.com": "a_uthor",
    "user2@gmail.com": "w_riter",
})

# Empty issue data map
NO_ISSUE_DATA = {}

COMMENT_ONE = {
    "content": "one",
    "id": 1,
    "published": "last year",
    "author": {"name": "user@email.com"},
    "updates": {
        "labels": ["added-label", "-removed-label"],
        },
}
COMMENT_TWO = {
    "content": "two",
    "id": 2,
    "published": "last week",
    "author": {"name": "user2@gmail.com"},
}
COMMENT_THREE = {
    "content": "three",
    "id": 3,
    "published": "yesterday",
    "author": {"name": "unknown@example.com"},
}
HTML_COMMENT = {
    "content": "1 &lt; 2",
    "id": 1,
    "published": "yesterday",
    "author": {"name": "unknown@example.com"},
}
COMMENTS_DATA = [
    COMMENT_ONE,
    {"content": "two", "id": 2, "published": "last week"},
    {"content": "three", "id": 3, "published": "yesterday"},
    {"content": "four", "id": 4, "published": "today"},
]
# Full issue json
ISSUE_JSON = {
    "id": 1,
    "state": "closed",
    "title": "issue_title",
    "comments": {"items": [COMMENT_ONE]},
    "labels": ["awesome", "great"],
    "published": "last year",
    "updated": "last month",
    "status": "Fixed",
    "owner": {
        "kind": "projecthosting#issuePerson",
        "name": "user@email.com",
    },
}

SINGLE_ISSUE = issues.GoogleCodeIssue(ISSUE_JSON, REPO, USER_MAP)

SINGLE_COMMENT = issues.GoogleCodeComment(SINGLE_ISSUE, COMMENT_ONE)
HTML_COMMENT = issues.GoogleCodeComment(SINGLE_ISSUE, HTML_COMMENT)

class GoogleCodeIssueTest(unittest.TestCase):
  """Tests for GoogleCodeIssue."""

  def testGetIssueOwner(self):
    # Report all issues coming from the person who initiated the
    # export.
    self.assertEqual("default_username", SINGLE_ISSUE.GetOwner())

  def testGetIssueOwnerNoOwner(self):
    issue_json = ISSUE_JSON.copy()
    del issue_json["owner"]
    issue = issues.GoogleCodeIssue(issue_json, REPO, USER_MAP)
    self.assertEqual("default_username", issue.GetOwner())

  def testGetIssueUserOwner(self):
    issue_json = copy.deepcopy(ISSUE_JSON)
    issue_json["owner"]["name"] = "notauser@email.com"
    issue = issues.GoogleCodeIssue(
        issue_json, REPO, USER_MAP)
    self.assertEqual(DEFAULT_USERNAME, issue.GetOwner())

  def testGetCommentAuthor(self):
    self.assertEqual("a_uthor", SINGLE_COMMENT.GetAuthor())

  def testGetCommentDescription(self):
    self.assertEqual(
        "```\none\n```\n\nOriginal issue reported on code.google.com by "
        "`a_uthor` on last year\n"
        "- **Labels added**: added-label\n"
        "- **Labels removed**: removed-label\n",
        SINGLE_COMMENT.GetDescription())

  def testGetHtmlCommentDescription(self):
    self.assertIn("```\n1 < 2\n```", HTML_COMMENT.GetDescription())

  def testTryFormatDate(self):
    self.assertEqual("last year", issues.TryFormatDate("last year"))
    self.assertEqual("2007-02-03 05:58:17",
                     issues.TryFormatDate("2007-02-03T05:58:17.000Z:"))
    self.assertEqual("2014-01-05 04:43:15",
                     issues.TryFormatDate("2014-01-05T04:43:15.000Z"))

  def testWrapText(self):
    self.assertEqual(issues.WrapText("0123456789", 3),
                     "0123456789")
    self.assertEqual(issues.WrapText("01234 56789", 3),
                     "01234\n56789")
    self.assertEqual(issues.WrapText("a b c d e f g h", 4),
                     "a b c\nd e f\ng h")

  def testLoadUserData(self):
    # Verify the "identity dictionary" behavior.
    user_data_dict = issues.LoadUserData(None, None)
    self.assertEqual(user_data_dict["chrs...@goog.com"], "chrs...@goog.com")


if __name__ == "__main__":
  unittest.main(buffer=True)
