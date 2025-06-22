from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, TextAreaField, FloatField, SelectField, IntegerField
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired
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

class MenuItemForm(FlaskForm):
    name = StringField("Cake Name", validators=[InputRequired()])
    price = FloatField("Price", validators=[InputRequired()])
    description = TextAreaField("Description")
    image = FileField("Image", validators=[FileAllowed(['jpg', 'png', 'jpeg'], "Images only!")])
    category = StringField('Category', validators=[InputRequired()])
    submit = SubmitField("Submit")

class OrderForm(FlaskForm):
    weight = FloatField("Weight (kg)", validators=[InputRequired()])
    shape = SelectField("Shape", choices=[('round', 'Round'), ('square', 'Square'), ('heart', 'Heart')])
    tiers = IntegerField("Tiers", validators=[InputRequired()])
    message = TextAreaField("Custom Message")
    delivery_mode = SelectField("Delivery Mode", choices=[('pickup', 'Pickup'), ('delivery', 'Home Delivery')])
    payment_mode = SelectField("Payment Mode", choices=[('cod', 'Cash on Delivery'), ('online', 'Online Payment')])
    submit = SubmitField("Place Order")


class BakerProfileForm(FlaskForm):
    bakery_name = StringField("Bakery Name", validators=[DataRequired()])
    phone = StringField("Phone", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    description = TextAreaField("Description")
    instagram = StringField("Instagram URL")
    facebook = StringField("Facebook URL")
    logo = FileField("Logo", validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    banner = FileField("Banner", validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField("Update Profile")

class BakerPricingForm(FlaskForm):
    base_price_per_kg = FloatField('Base Price per Kg', validators=[DataRequired()])
    extra_tier_price = FloatField('Extra Tier Price', validators=[DataRequired()])
    frosting_prices = TextAreaField('Frosting Prices (JSON format)', validators=[DataRequired()])
    topper_prices = TextAreaField('Topper Prices (JSON format)', validators=[DataRequired()])
    submit = SubmitField('Save Pricing')

