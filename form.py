from flask_wtf import FlaskForm  # Importing FlaskForm base class for creating forms.
from wtforms import StringField, SubmitField  # Importing specific field types.


# Form for querying total spending by a user's ID.
class TotalSpentById(FlaskForm):
    # A text field for the user ID input.
    user_id = StringField(
        label="Total Spent By User ID",  # Label displayed with the field.
        render_kw={  # Additional attributes for rendering the field in HTML.
            "style": "width: 150px;",  # CSS styling for width.
            "placeholder": "Enter User ID"  # Placeholder text in the input field.
        }
    )
    # A submit button to trigger the form submission.
    submit = SubmitField(label="Search")


# Form for adding a new user with their total spending.
class AddNewUser(FlaskForm):
    # A text field for entering the user ID.
    user_id = StringField(
        label="User ID",  # Label displayed with the field.
        render_kw={  # Additional attributes for rendering the field in HTML.
            "style": "width: 150px;",  # CSS styling for width.
            "placeholder": "Enter User ID"  # Placeholder text in the input field.
        }
    )
    # A text field for entering the total spending.
    total_spent = StringField(
        label="Total Spent",  # Label displayed with the field.
        render_kw={  # Additional attributes for rendering the field in HTML.
            "style": "width: 150px;",  # CSS styling for width.
            "placeholder": "Enter Value"  # Placeholder text in the input field.
        }
    )
    # A submit button to trigger the form submission.
    submit = SubmitField(label="Submit")
