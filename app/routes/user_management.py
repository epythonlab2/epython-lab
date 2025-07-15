@app.route("/api/admin/users", methods=["GET"])
def api_get_users():
    # Return paginated user list

@app.route("/api/admin/users/<int:user_id>", methods=["GET", "PUT", "DELETE"])
def api_user_detail(user_id):
    # Get, update or delete user

@app.route("/api/admin/users", methods=["POST"])
def api_create_user():
    # Create new user
