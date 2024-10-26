from database import create_table, insert_user, read_users, delete_user

# Step 1: Create the table if it does not exist
create_table()

# Step 2: Insert a user
result = delete_user(email="yatndeep@vunetsystems.com")
print(result)  # Should show success or an error message

# Step 3: Read users
users = read_users()
print(users)  # Should show Alice in the list
