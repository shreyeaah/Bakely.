from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, TextAreaField, FloatField
from wtforms.validators import InputRequired, Length, ValidationError
from models import User
from flask_wtf.file import FileField, FileAllowed

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)],
                             render_kw={"placeholder": "Password"})
    role = RadioField('Register as', choices = [('customer','Customer'), ('baker','Baker')], validators = [InputRequired()])

    bakery_name = StringField('Bakery Name', render_kw={"placeholder": "Bakery Name"})
    phone = StringField('Phone Number', render_kw={"placeholder": "Phone Number"})
    address = TextAreaField('Address', render_kw={"placeholder": "Bakery Address"})
    description = TextAreaField('Description', render_kw={"placeholder": "Bakery Description"})

    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user = User.query.filter_by(username=username.data).first()
        if existing_user:
            raise ValidationError("Username already exists. Please choose a different one.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)],
                             render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

class ApproveForm(FlaskForm):
    submit = SubmitField('Approve')

class DeclineForm(FlaskForm):
    submit = SubmitField('Decline')

'''class MenuItemForm(FlaskForm):
    name = StringField("Cake Name", validators=[InputRequired()])
    price = FloatField("Price", validators=[InputRequired()])
    description = TextAreaField("Description")
    image = FileField("Image", validators=[FileAllowed(['jpg', 'png', 'jpeg'], "Images only!")])
    submit = SubmitField("Add Menu Item")'''