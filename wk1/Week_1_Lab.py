# HOO ZI HAO (2603028)

#region Activity 1
def print_Act1(message, char="="):
    divider = char * len(message)
    print(f"{divider}\n{message}\n{divider}")

Act1Msg = "What am I doing in this course?"
#print_Act1(Act1Msg)
#endregion 

#region Activity 2
def hardcodedAct2():
    username ="John Doe"
    bio = "I am a software developer with a passion for learning new technologies."
    followers = 150

    info = [
    f"Username: {username}",
    f"Bio: {bio}",
    f"Followers: {followers}"]
    print("\n".join(info))

hardcodedAct2()
#endregion