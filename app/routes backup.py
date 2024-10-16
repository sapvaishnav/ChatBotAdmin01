from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from app.models.UserModel import UserModel  # Update this import according to your models.py structure
from app.models.TenantModel import TenantModel
from app.models.ChatbotLeadModel import ChatbotLeadModel
from app.models.BotConfigurationModel import BotConfigurationModel 
from app.models.DataAugmentationModel import DataAugmentationModel
import re
# Create a Blueprint for the routes
routes = Blueprint('routes', __name__)

# Route for the index page
@routes.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        flash('An error occurred while loading the index page: {}'.format(e), 'danger')
        return redirect(url_for('routes.index'))

@routes.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            # Ensure username and password are provided
            if not username or not password:
                flash('Username and password are required.', 'danger')
                return redirect(url_for('routes.login'))

            # Verify user credentials
           
            result = UserModel.verify_user(username, password)

            if result is True:
              
                session['username'] = username
              
                return redirect(url_for('routes.dashboard'))
            else:
                # Display the specific error message returned from `verify_user`
                flash(result, 'danger')

        # GET request or after failed login attempt
        return render_template('login_register/login.html')

    except Exception as e:
        # Log the exception for debugging (optional)
        print(f"Error occurred during login: {str(e)}")
        
        # Flash a generic error message
        flash('Please try again later.', 'danger')
        return redirect(url_for('routes.login'))

# Route for user registration
@routes.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            email = request.form.get('email')

            # Check if the passwords match
            if password != confirm_password:
                flash('Passwords do not match!', 'danger')
                return redirect(url_for('routes.register'))

            # Validate username: No spaces, less than 20 characters
            if not UserModel.validate_username(username):
                flash('Username must not contain spaces and should be less than 20 characters!', 'danger')
                return redirect(url_for('routes.register'))

            # Validate password: At least 1 uppercase, 1 lowercase, 1 digit, more than 8 characters
            if not UserModel.validate_password(password):
                flash('Password must contain at least one uppercase letter, one lowercase letter, one digit, and be longer than 8 characters!', 'danger')
                return redirect(url_for('routes.register'))

            # Add user to the database
            result = UserModel.add_user(username, password, email)  # Returns True on success, None or False on failure

            if result is None:
                flash("Registration failed. User might already exist or there was an issue with tenant creation.", "danger")
                return redirect(url_for('routes.register'))

            if result:
                flash('Registration successful! You can now log in.', 'success')
                return redirect(url_for('routes.login'))
            else:
                flash('Registration failed. Please try again.', 'danger')

        return render_template('login_register/register.html')
    
    except Exception as e:
        print(f"Error: {str(e)}")
        flash('Please Try Again : {}'.format(e), 'danger')
        return redirect(url_for('routes.register'))


# Route for the dashboard
@routes.route('/dashboard')
def dashboard():
    try:
        return render_template('/dashboard/dashboard.html')
    except Exception as e:
        flash('An error occurred while loading the dashboard: {}'.format(e), 'danger')
        return redirect(url_for('routes.dashboard'))

# Route for user logout
@routes.route('/logout')
def logout():
    try:
        session.pop('username', None)  # Remove user from session
        flash('You have been logged out.', 'info')
        return redirect(url_for('routes.login'))
    except Exception as e:
        flash('An error occurred while logging out: {}'.format(e), 'danger')
        return redirect(url_for('routes.dashboard'))

# Route for leads page
@routes.route('/leads')
def leads():
    tenant_id = session.get('tenant_id')
    try:
        print(f"test  {tenant_id}")
        leads = ChatbotLeadModel.get_all_leads(tenant_id)  # Fetch all leads for the tenant
        return render_template('organization/leads.html', leads=leads)  # Pass leads to the template
    except Exception as e:
        flash('An error occurred while loading the leads page: {}'.format(e), 'danger')
        return redirect(url_for('routes.leads'))
    # Route for data augmentation page


@routes.route('/dataaugmentation', methods=['GET', 'POST'])
def data_augmentation():
    tenant_id = session.get('tenant_id')
    if request.method == 'POST':
        # Handle the form submission to add a new document
        document_name = request.form.get('document_name')
        document_type = request.form.get('document_type')
        document_status = request.form.get('document_status')
        

        # Validate input fields before adding a document
        if not document_name or not document_type or not document_status or not tenant_id:
            flash('All fields are required!', 'danger')
            return redirect(url_for('routes.data_augmentation'))

        doc_id = DataAugmentationModel.add_document(document_name, document_type, document_status, tenant_id)
        if doc_id:
            flash('Document added successfully!', 'success')
        else:
            flash('Failed to add document.', 'danger')

        return redirect(url_for('routes.data_augmentation'))

    # Handle GET request to display existing documents
    documents = DataAugmentationModel.get_all_documents(tenant_id) 
    Urls = DataAugmentationModel.get_all_urls(tenant_id) 
    databaseconnection = DataAugmentationModel.get_all_db_connection(tenant_id)  # Method to get all documents
    return render_template('data_augmentation/data_augmentation.html', documents=documents,Urls=Urls,databaseconnection=databaseconnection)


# Route for agents page
@routes.route('/agents')
def agents():
    try:
        return render_template('organization/agents.html')
    except Exception as e:
        flash('An error occurred while loading the agents page: {}'.format(e), 'danger')
        return redirect(url_for('routes.agents'))

@routes.route('/bot_config', methods=['GET', 'POST'])
def bot_config():
    tenant_id = session.get('tenant_id')

    if request.method == 'POST':
        try:
            print(f"tenant_id = {tenant_id}")
            
            # Handle bot avatar file upload
            bot_avatar_file = request.files.get('input_bot_avatar')
            bot_avatar_filename = bot_avatar_file.filename if bot_avatar_file else None
            '''if bot_avatar_file:
                bot_avatar_filepath = os.path.join('path_to_save_avatar', bot_avatar_filename)
                bot_avatar_file.save(bot_avatar_filepath)'''
            print(f"bot_avatar_filename = {bot_avatar_filename}")

            # Handle workspace background file upload
            workspace_bg_file = request.files.get('input_workspace_background')
            workspace_bg_filename = workspace_bg_file.filename if workspace_bg_file else None
            '''if workspace_bg_file:
                workspace_bg_filepath = os.path.join('path_to_save_workspace_bg', workspace_bg_filename)
                workspace_bg_file.save(workspace_bg_filepath)'''
            print(f"workspace_bg_filename = {workspace_bg_filename}")

            # Pass form values directly to the update function
            updated = BotConfigurationModel.update_configuration(
                
                tenant_id=tenant_id,
                model_name=request.form.get('input_model_name'),
                model_key=request.form.get('input_model_key'),
                creativity=float(request.form.get('input_creativity', 0.1)),
                threshold=float(request.form.get('input_threshold', 0.1)),
                bot_name=request.form.get('input_bot_name'),
                bot_avatar=bot_avatar_filename,
                bot_workspace=workspace_bg_filename,
                short_term_memory_length=int(request.form.get('input_short_term_memory', 0)),
                max_matching_knowledge=int(request.form.get('input_max_matching_knowledge', 0)),
                greeting_message=request.form.get('input_greeting_message', ''),
                static_message=request.form.get('input_static_message', '')
            )
            
            if updated:
                flash('Bot configuration updated successfully!', 'success')
            else:
                flash('No changes made to the configuration or an error occurred.', 'warning')

        except ValueError as ve:
            flash(f'Invalid input for creativity or threshold: {str(ve)}', 'danger')
        except Exception as e:
            flash(f'An error occurred while updating the bot configuration: {str(e)}', 'danger')

        return redirect(url_for('routes.bot_config'))

    # Handle GET request
    try:
        # Retrieve the mapped configuration for the tenant
        config = BotConfigurationModel.get_configuration(tenant_id)
        print(f"config == {config}")
        return render_template('chat/bot_configuration.html', config=config)  # Pass the config to the template

    except Exception as e:
        flash(f'An error occurred while loading the bot configuration page: {str(e)}', 'danger')
        return redirect(url_for('routes.bot_config'))  # Redirect to the same page on error
    
 


# Route for billing and usage page
@routes.route('/billing')
def billing():
    try:
        return render_template('organization/billing.html')
    except Exception as e:
        flash('An error occurred while loading the billing page: {}'.format(e), 'danger')
        return redirect(url_for('routes.billing'))

# Route for reports page
@routes.route('/reports')
def reports():
    try:
        return render_template('organization/reports.html')
    except Exception as e:
        flash('An error occurred while loading the reports page: {}'.format(e), 'danger')
        return redirect(url_for('routes.reports'))

@routes.route('/orgprofile', methods=['GET', 'POST'])
def org_profile():
    try:
        tenant_id = session.get('tenant_id')
       # print(f"tenant_id = {tenant_id}")
        
        # Check if tenant_id is not set
        if tenant_id is None:
            flash('Invalid session. You have been logged out.', 'danger')
            session.clear()  # Clear the session
            return redirect(url_for('routes.login'))  # Redirect to login page

        # Fetch organization data based on tenant_id
        data = TenantModel.get_tenant(tenant_id)
        #print(f"data = {data}")

        if data is None:
            #print(f"No organization found for tenant_id.")
            flash('No organization found for the provided Tenant ID. You have been logged out.', 'warning')
            session.clear()  # Clear the session
            return redirect(url_for('routes.login'))  # Redirect to login page

        # Handle form submission for updating tenant data
        if request.method == 'POST':
            tenant_name = request.form.get('tenant_name')
            tenant_contact = request.form.get('tenant_contact')
            tenant_emailid = request.form.get('tenant_emailid')
            tenant_address = request.form.get('tenant_address')
            tenant_city = request.form.get('tenant_city')
            tenant_country = request.form.get('tenant_country')
            tenant_postcode = request.form.get('tenant_postcode')
            tenant_GSTNNo = request.form.get('tenant_GSTNNo')
            tenant_PAN = request.form.get('tenant_PAN')
           

            # Update tenant information
            if TenantModel.update_tenant(
                tenant_id,
                tenant_name,
                tenant_address,
                tenant_emailid,
                tenant_contact,
                tenant_city,
                tenant_country,
                tenant_postcode,
                tenant_GSTNNo,
                tenant_PAN
            ):
                # Fetch updated data after successful update
                data = TenantModel.get_tenant(tenant_id)
                #print(f"Organization information updated successfully.")
                flash('Organization information updated successfully.', 'success')
            else:
                data = None
                #print(f"Failed to update organization information")
                flash('Failed to update organization information.', 'danger')

        # Render the organization info page for GET requests or after a failed POST
        return render_template('organization/organization_info.html', tenant=data)

    except Exception as e:
       # print(f"Error  {str(e)}")
        flash('An error occurred while loading the organization profile page: {}'.format(e), 'danger')
        session.clear()  # Clear the session on error
        return redirect(url_for('routes.login'))  # Redirect to login page



    
# Route for support page
@routes.route('/support')
def support():
    try:
        return render_template('organization/support.html')
    except Exception as e:
        flash('An error occurred while loading the support page: {}'.format(e), 'danger')
        return redirect(url_for('routes.support'))

# Route for smart chat (ChatGPT-like interface)
@routes.route('/smart_chat')
def smart_chat():
    try:
        return render_template('chat/smart_chat.html')
    except Exception as e:
        flash('An error occurred while loading the smart chat page: {}'.format(e), 'danger')
        return redirect(url_for('routes.smart_chat'))

# Route for quick chat (simple, compact version)
@routes.route('/quick_chat')
def quick_chat():
    try:
        return render_template('chat/quick_chat.html')
    except Exception as e:
        flash('An error occurred while loading the quick chat page: {}'.format(e), 'danger')
        return redirect(url_for('routes.quick_chat'))

# Route for sidebar chatbot
@routes.route('/sidebar_chat')
def sidebar_chat():
    try:
        return render_template('chat/sidebar_chat.html')
    except Exception as e:
        flash('An error occurred while loading the sidebar chat page: {}'.format(e), 'danger')
        return redirect(url_for('routes.sidebar_chat'))
