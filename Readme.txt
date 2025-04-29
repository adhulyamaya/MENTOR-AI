pip install virtualenv

virtualenv venv

venv\Scripts\activate (windows)

pip install -r requirements.txt

python manage.py makemigrations

python manage.py migrate

python manage.py runserver


The server will be running on http://127.0.0.1:8000/


## Available API Endpoints

Here is a list of available URLs for your project:
---------------------------------------------------
### Authentication and User Management

- **Login**  
  `POST` `http://127.0.0.1:8000/login`  
  Logs in the user.

- **Logout**  
  `GET` `http://127.0.0.1:8000/logout/`  
  Logs out the user.

- **Register**  
  `POST` `http://127.0.0.1:8000/register/`  
  Registers a new user.

- **User Dashboard**  
  `GET` `http://127.0.0.1:8000/user_dashboard/`  
  Shows the user's dashboard.

- **User Profile**  
  `GET` `http://127.0.0.1:8000/user_profile/`  
  Displays the user's profile.

- **Edit Profile**  
  `GET` `http://127.0.0.1:8000/edit_profile/`  
  Allows the user to edit their profile.

- **Settings**  
  `GET` `http://127.0.0.1:8000/settings/`  
  Accesses user settings.

### Content and Static Pages

- **Pricing**  
  `GET` `http://127.0.0.1:8000/pricing/`  
  Displays pricing details.

- **Features**  
  `GET` `http://127.0.0.1:8000/features/`  
  Shows the features of the app.

- **Contact**  
  `GET` `http://127.0.0.1:8000/contact/`  
  Provides contact details.

- **Try Free**  
  `GET` `http://127.0.0.1:8000/try_free/`  
  Allows the user to try the service for free.

- **Terms of Service**  
  `GET` `http://127.0.0.1:8000/terms/`  
  Displays the terms of service.

- **Privacy Policy**  
  `GET` `http://127.0.0.1:8000/privacy_policy/`  
  Shows the privacy policy.

### Payment and Subscription

- **Payment Page**  
  `GET` `http://127.0.0.1:8000/payment/`  
  Displays the payment page.

- **Subscribe to Plan**  
  `GET` `http://127.0.0.1:8000/subscribe/<str:plan_key>/`  
  Subscribe to a specific plan (replace `<str:plan_key>` with the actual plan key).

- **Confirm Payment**  
  `GET` `http://127.0.0.1:8000/confirm/`  
  Confirms the payment.

- **Success Page**  
  `GET` `http://127.0.0.1:8000/success/`  
  Displays the payment success page.

- **Error Page**  
  `GET` `http://127.0.0.1:8000/error/`  
  Displays the payment error page.

### Search

- **Search**  
  `GET` `http://127.0.0.1:8000/search/`  
  Allows users to search for content.

---

**Note**: Replace `127.0.0.1:8000` with your actual server URL 