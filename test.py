#!/Users/amitm/sample/venv-pythonProject/bin/python3.7
#test
f = open(".gitignore", "r")
lines=f.readlines()
X_JFrog_Art_Api = lines[0].strip()
User_Name = lines[1].strip()
User_Password = lines[2].strip()
f.close()