"""
Set of functions to interact with the history database
"""

from . import User as UserDB
from tinydb.operations import add, increment
from tinydb import Query
from telegram import User


class Users:
    """
    Ease of access interface for the User db
    """

    @staticmethod
    def ensure_exists(user: User):
        user_id = user.id
        name = user.full_name

        # insert or update data
        result_user = UserDB.get(Query().id == user_id)
        if result_user is None:
            UserDB.insert(
                {
                    "id": user_id,
                    "name": name,
                    "donated": 0,
                    "views": 0,
                }
            )
            result_user = UserDB.get(Query().id == user_id)
        return result_user

    @staticmethod
    def donation(user_telegram, amt):
        """
        Donate or "undonate"

        returns false if there was an issue:
            - Undonate more than was donated
        """
        user = Users.ensure_exists(user_telegram)

        if user["donated"] + amt < 0:
            return False
        UserDB.update(add("donated", amt), Query().id == user_telegram.id)
        return True

    @staticmethod
    def get_donation(user_telegram):
        user = Users.ensure_exists(user_telegram)

        return user["donated"]

    @staticmethod
    def view(user_telegram):
        """
        record viewing the oats
        """
        Users.ensure_exists(user_telegram)
        UserDB.update(increment("views"), Query().id == user_telegram.id)

    @staticmethod
    def get_total_donations():
        return sum([user["donated"] for user in UserDB.all()])

    @staticmethod
    def views_to_message(page=0, per_page=10):
        od = sorted(UserDB.all(), key=lambda u: u["views"])
        od.reverse()

        if len(od) == 0:
            return False

        res = "<b>O A T S   Leaderboard:</b>\n"
        start = page * per_page

        for i, user in enumerate(od[start:]):
            if i >= 10:
                break
            res += "<b>{}</b>:\t{} has viewed {} O A T S!\n".format(
                i + 1, user["name"], user["views"]
            )

        if res == "<b>O A T S   Leaderboard:</b>\n":
            return "Invalid page argument."
        return res

    @staticmethod
    def donations_to_message(page=1, per_page=10):
        total = Users.get_total_donations()
        if total == 0:
            return
