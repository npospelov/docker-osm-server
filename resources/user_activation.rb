user = User.find_by_display_name("test")
user.status = "active"
user.save!
