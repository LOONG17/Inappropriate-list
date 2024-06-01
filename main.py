import requests
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

def get_user_info(user_id):
    url = f"https://users.roblox.com/v1/users/{user_id}"
    response = requests.get(url)
    if response.status_code == 200:
        user_data = response.json()
        print("User ID:", user_data["id"])
        print("Username:", user_data["name"])
        print("Display Name:", user_data["displayName"])
        print("Description:", user_data["description"])
        print("Created:", user_data["created"])
        print("Banned:", user_data["isBanned"])
        print("Verified Badge:", user_data["hasVerifiedBadge"])
        print("="*50)
        return user_data
    else:
        print("Error occurred while fetching user information. Status code:", response.status_code)
        return None

def get_friends(user_id):
    url = f"https://friends.roblox.com/v1/users/{user_id}/friends"
    response = requests.get(url)
    if response.status_code == 200:
        friends_data = response.json()["data"]
        friends_list = [(friend["id"], friend["name"], friend["displayName"]) for friend in friends_data]
        return friends_list
    else:
        print("Error occurred while fetching user's friends. Status code:", response.status_code)
        return []

def get_groups(user_id):
    url = f"https://groups.roblox.com/v1/users/{user_id}/groups/roles"
    response = requests.get(url)
    if response.status_code == 200:
        groups_data = response.json()["data"]
        groups_list = [(group["group"]["id"], group["group"]["name"]) for group in groups_data]
        return groups_list
    else:
        print("Error occurred while fetching user's groups. Status code:", response.status_code)
        return []

def find_common_groups(user_id, num_friends):
    friends_list = get_friends(user_id)
    common_groups = {}
    for friend_id, _, _ in friends_list:
        friend_groups = get_groups(friend_id)
        for group_id, group_name in friend_groups:
            if group_id not in common_groups:
                common_groups[group_id] = {"name": group_name, "count": 1}
            else:
                common_groups[group_id]["count"] += 1
    common_groups = {group_id: group_data for group_id, group_data in common_groups.items() if group_data["count"] >= num_friends}
    return common_groups

def load_filtered_words(filename):
    with open(filename, "r") as file:
        filtered_words = [word.strip() for word in file.readlines()]
    return filtered_words

def check_for_flagged_words(name, filtered_words):
    for word in filtered_words:
        if word.lower() in name.lower():
            return True
    return False

def check_banned_users(user_ids):
    for user_id in user_ids:
        url = f"https://users.roblox.com/v1/users/{user_id}"
        response = requests.get(url)
        if response.status_code == 200:
            user_data = response.json()
            if user_data["isBanned"]:
                print(Fore.RED + "User ID:", user_data["id"])
                print("Username:", user_data["name"])
                print("Banned:", user_data["isBanned"])
                print("-"*50)
        else:
            print(Fore.RED + f"Error occurred while checking user {user_id}. Status code:", response.status_code)
            print("-"*50)

def check_single_user_banned(user_id):
    url = f"https://users.roblox.com/v1/users/{user_id}"
    response = requests.get(url)
    if response.status_code == 200:
        user_data = response.json()
        print("User ID:", user_data["id"])
        print("Username:", user_data["name"])
        print("Banned:", user_data["isBanned"])
        print("="*50)
    else:
        print("Error occurred while fetching user information. Status code:", response.status_code)

def search_friend_list(friends_list, filtered_words):
    flagged_friends = []
    print("Flagged Friends:")
    for index, friend_data in enumerate(friends_list, start=1):
        friend_id, friend_name, friend_display_name = friend_data
        flagged = check_for_flagged_words(friend_name, filtered_words) or check_for_flagged_words(friend_display_name, filtered_words)
        if flagged:
            flagged_friends.append(friend_data)
            print(Fore.RED + f"{index}. Friend ID: {friend_id} | Username: {friend_name} | Display Name: {friend_display_name}")
            print("-"*50)
    if not flagged_friends:
        print("No flagged friends found.")
    return flagged_friends

def main(user_id):
    num_friends_required = 3
    filtered_words = load_filtered_words("fools.txt")
    print("="*50)
    user_info = get_user_info(user_id)
    if user_info:
        friends_list = get_friends(user_id)
        print("Friends List:")
        for friend_id, friend_name, friend_display_name in friends_list:
            flagged = check_for_flagged_words(friend_name, filtered_words) or check_for_flagged_words(friend_display_name, filtered_words)
            if flagged:
                print(Fore.RED + "⚠Flagged" + Style.RESET_ALL)
                print(Fore.RED + "Friend ID:", friend_id)
                print("Friend Username:", friend_name)
                print("Friend Display Name:", friend_display_name)
            else:
                print("Friend ID:", friend_id)
                print("Friend Username:", friend_name)
                print("Friend Display Name:", friend_display_name)
            print("-"*50)
        print("="*50)

        common_groups = find_common_groups(user_id, num_friends_required)
        if common_groups:
            print("Groups with at least", num_friends_required, "friends:")
            for group_id, group_data in common_groups.items():
                print("Group ID:", group_id)
                print("Group Name:", group_data["name"])
                print("Count:", group_data["count"])
                print("-"*50)
        else:
            print("No groups found with at least", num_friends_required, "friends in common.")

        print("Select an option:")
        print("1. Bancheck Friends List")
        print("2. Bancheck Single User")
        print("3. Search Friend List")
        option = input("Enter your choice: ")

        if option == "1":
            banned_user_ids = [friend[0] for friend in friends_list if friend[0] is not None]
            check_banned_users(banned_user_ids)
        elif option == "2":
            user_id_to_check = input("Enter the user ID to check: ")
            check_single_user_banned(user_id_to_check)
        elif option == "3":
            flagged_friends = search_friend_list(friends_list, filtered_words)
            if flagged_friends:
                serial_number = int(input("Enter the serial number of the flagged friend to search: "))
                if 1 <= serial_number <= len(flagged_friends):
                    friend_id_to_search = flagged_friends[serial_number - 1][0]
                    main(friend_id_to_search)
                else:
                    print("Invalid serial number.")
        else:
            print("Invalid option.")

if __name__ == "__main__":
    user_id = input("Enter Roblox user ID: ")
    main(user_id)
