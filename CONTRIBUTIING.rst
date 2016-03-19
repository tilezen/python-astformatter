If you would like to contribute changes or new content, please feel free!  But please follow these guidelines...

1.  Always create your changes or new content in a "topic" branch whose name is descriptive of the changes.
2.  If the changes you're submitting are related to a submitted Issue, include the issue number in the branch name.  (e.g. ``issue-0001-foo-bar-baz``)
3.  Please make sure you run ``git diff --check`` to check for trailing whitespace.

Bonus points - ``behave`` testing:
You must have the ``behave`` python package installed for these steps to work.

4.  Add new behave tests and/or scenarios that validate the new or fixed functionality (in ``tests/features/astformatter.feature``).
5.  Ensure your changes pass all existing and new ``behave`` tests.
