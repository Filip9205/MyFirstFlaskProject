import threading

# Flask and other necessary libraries
from flask import Flask, render_template, redirect, url_for, request
from data_base import DataBase, UsersData
from flask_paginate import Pagination, get_page_args
from form import TotalSpentById, AddNewUser
from flask_bootstrap import Bootstrap5
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "random key"  # Secret key for Flask sessions

# Telegram bot token and initialization
BOT_TOKEN = '7802243056:AAGPi-lxI-NhnZ8lQWDjX9Rjohx8BTzv57Y'
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Set up logging for bot
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


# Command handler for the "/start" command in Telegram bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Send a welcome message with available commands
    await update.message.reply_text(
        "Welcome! Use /total_spent <user_id> to get total spending of a user.\n"
        "Use /average_spent to see the average spending by age groups."
    )


# Command handler for the "/total_spent" command in Telegram bot
async def total_spent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if exactly one argument (user ID) is passed
    if len(context.args) != 1:
        await update.message.reply_text("Please provide a user ID. Example: /total_spent 1")
        return

    try:
        # Try to convert the argument to an integer (user ID)
        user_id = int(context.args[0])
        # Fetch total spending data for the user from the database
        user = db.total_spend_by_user_id(user_id)
        print(user)
        if user:
            # Send the total spending data for the user
            await update.message.reply_text(f"User ID: {user['id']}\nTotal Spent: {user['total_money_spent']}")
        else:
            await update.message.reply_text("No data found for this user!")
    except ValueError:
        # Handle invalid user ID (non-integer)
        await update.message.reply_text("Invalid ID. Please provide a numeric user ID.")


# Command handler for the "/average_spent" command in Telegram bot
async def average_spent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Fetch average spending data by age group
    avg_data = db.avg_spend()
    if avg_data:
        # Format the response as a list of age groups with their average spending
        response = "\n".join([f"Age Group: {data[0]}, Average Spend: {data[1]}" for data in avg_data])
        await update.message.reply_text(f"Average Spending by Age:\n{response}")
    else:
        await update.message.reply_text("No average spending data available.")


# Add the command handlers to the Telegram bot application
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("total_spent", total_spent))
telegram_app.add_handler(CommandHandler("average_spent", average_spent))

# Initialize database and Flask-Bootstrap
db = DataBase()
bootstrap = Bootstrap5(app)


# Home page route
@app.route("/")
def home_page():
    return render_template("home_page.html")


# All users page route with pagination
@app.route("/all_users", methods=["GET", "POST"])
def all_users():
    form = TotalSpentById()  # Form for user ID search
    get_all_users = db.all_users()  # Fetch all users from the database
    users_obj = []

    # Create UsersData objects for each user
    for user in get_all_users:
        new_user = UsersData(id=user[0], name=user[1], mail=user[2], age=user[3])
        users_obj.append(new_user)

    # Pagination setup
    page, per_page, offset = get_page_args()
    total = len(users_obj)
    pagination_users = users_obj[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=total)

    # If form is submitted, process total spending by user ID
    if form.validate_on_submit():
        return total_spent(form.user_id.data)

    # Render the all users page with pagination and the form
    return render_template("all_users.html", users=pagination_users, pagination=pagination, form=form)


# User information page route
@app.route("/user/<int:user_id>")
def user_info(user_id):
    # Fetch user info by ID
    if db.user_info_by_id(user_id):
        user = db.user_info_by_id(user_id)
        new_user = UsersData(id=user[0], name=user[1], mail=user[2], age=user[3])
        return render_template("user_by_id.html", user=new_user, data=True)
    else:
        return render_template("user_by_id.html", data=False, user_id=user_id)


# Total spent by user ID page route
@app.route("/total_spent/<int:user_id>")
def total_spent(user_id):
    # Fetch total spent by the user from the database
    if db.total_spend_by_user_id(user_id):
        user = db.total_spend_by_user_id(user_id)
        return render_template("total_spent.html", user=user, data=True)
    else:
        return render_template("total_spent.html", data=False, user_id=user_id)


# Average spending by age group page route
@app.route("/average_spending_by_age")
def average_spent():
    # Fetch average spending by age groups
    avg_data = db.avg_spend()
    age_groups_obj = []
    for data in avg_data:
        new_age_group = UsersData(age=data[0], average=data[1])
        age_groups_obj.append(new_age_group)

    # Render the average spending by age page
    return render_template("average_spent.html", age_groups=age_groups_obj)


# High spenders page route with form to add new high spenders
@app.route("/high_spenders.html", methods=["POST", "GET"])
def high_spenders():
    form = AddNewUser()  # Form to add a new high spender
    high_spenders_data = db.get_high_spenders()  # Fetch all high spenders
    high_spenders_obj = []

    # Create UsersData objects for high spenders
    for data in high_spenders_data:
        new_high_spender = UsersData(id=data[0], average=data[1])
        high_spenders_obj.append(new_high_spender)

    # If form is submitted, add the new high spender to the database
    if form.validate_on_submit():
        user_id = form.user_id.data
        spent = form.total_spent.data
        DataBase().add_new_high_spender(id=user_id, total_spent=spent)
        return redirect(url_for("high_spenders"))
    else:
        # Render the high spenders page
        return render_template("high_spenders.html", users=high_spenders_obj, form=form)


# Webhook route to handle incoming Telegram messages
@app.route("/webhook", methods=["POST"])
def webhook():
    # Convert the incoming JSON payload to a Telegram Update object
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    # Put the update into the bot's update queue for processing
    telegram_app.update_queue.put(update)
    return "OK", 200


# Run the Flask app and Telegram bot
if __name__ == "__main__":
    # Start the Flask web app
    app.run(debug=True)
    # Start the Telegram bot polling loop
    telegram_app.run_polling()
