# HOO ZI HAO (2603028)

#region Imports
import textwrap
#endregion

#region Global Variables
Act1Msg = "What am I doing in this course?"
username = ""
bio = ""
followers = 0
age = 0
category = ""
#endregion

#region Activity 1
def print_formattedHeader(message, char="="):
    divider = char * len(message)
    print(f"{divider}\n{message}\n{divider}")
#endregion 

#region Activity 2
def hardcodedAct2():
    global username, bio, followers
    username ="John Doe"
    bio = "I am a software developer with a passion for learning new technologies."
    followers = 150

    info = [
        f"Username: {username}",
        f"Bio: {bio}",
        f"Followers: {followers}"]
    print("\n".join(info))
#endregion

#region Activity 3
def FollowerGrowthAct3():
    followers= 100

    followers += 50
    print("Day 1: Followers =", followers)

    followers += 20
    print("Day 2: Followers =", followers) 

    followers -= 10
    print("Day 3: Followers =", followers)
#endregion

#region Activity 4
def UserProfileAct4():
    global username, age, category
    username = input("Enter your username: ")
    age = int(input("Enter your age: "))
    category = input("Enter your category (e.g., Tech, Lifestyle, etc.): ")

    title = "Instagram User Profile"
    divider = "=" * len(title)

    formatted_profile = textwrap.dedent(f"""
        {title}
        {divider}
        Username: {username}
        Age: {age}
        Category: {category}
    """).strip()

    print(formatted_profile)
#endregion

#region Activity 5
def SomethingFunAct5():
    UserProfileAct4()
    global age, category
    funnyMsg = "What's exciting to you these days? A good coupon?"
    if age>= 40 and category.lower() == "fun":
        print(funnyMsg)
#endregion

#region Main Function
def run_activity(activity_name, activity_function):
    print_formattedHeader(activity_name)
    activity_function()
    print()

def main():
    run_activity("ACTIVITY 1", lambda: print_formattedHeader(Act1Msg))
    run_activity("ACTIVITY 2", hardcodedAct2)
    run_activity("ACTIVITY 3", FollowerGrowthAct3)
    run_activity("ACTIVITY 4 & 5", SomethingFunAct5)

if __name__ == "__main__":
    main()

#endregion