# HOO ZI HAO (2603028)

#region Global Variables
Act1Msg = "What am I doing in this course?"
username = ""
bio = ""
followers = 0
age = 0
category = ""
#endregion

#region Activity 1
def print_Act1(message, char="="):
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