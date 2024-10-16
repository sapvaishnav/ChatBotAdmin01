from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from app.models.UserModel import UserModel  # Update this import according to your models.py structure
from app.models.TenantModel import TenantModel
from app.models.ChatbotLeadModel import ChatbotLeadModel
from app.models.BotConfigurationModel import BotConfigurationModel 
from app.models.DataAugmentationModel import DataAugmentationModel
from app.models.TrainingModel import TrainingModel
import re
import os 
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
    
@routes.route('/upload_single_document', methods=[  'POST'])
def upload_single_document():
    """Handles the upload of a single document."""
    try:
        tenant_id = session.get('tenant_id')
        # Get the single file instead of a list
        file = request.files.get('files')  # Change getlist to get

        # Ensure the uploads directory exists
        uploads_dir = 'uploads/'+str(tenant_id)+'/dataaugmentation/'
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)

        if file:  # Check if a file is provided
            print(f"file: {file.filename}")

            # Save the file to the server
            file_path = os.path.join(uploads_dir, file.filename)
            file.save(file_path)  # Save the file
            
            # Extract document name, type, and status
            document_name = file.filename
            document_type = document_name.rsplit('.', 1)[1].lower() if '.' in document_name else 'unknown'
            document_status = "Uploaded"
           # print(f"document_name: {document_name}")

            # Validate input fields before adding a document
            if not document_name or not document_type or not document_status:
                return flash(f'All fields are required!', 'danger')  

            # Add document to the database
            message = DataAugmentationModel.add_document(document_name, document_type, document_status, tenant_id)
           # print(f"message: {message}")
            return message
        
        return  flash(f'No file uploaded.', 'danger')   

    except Exception as e:
        return  flash(f'An error occurred while uploading the document: {str(e)}', 'danger')   
    


@routes.route('/remove_document', methods=['POST'])
def remove_document():
    try:
        document_id = request.form.get('document_id')
        tenant_id = session.get('tenant_id')

          # Call the delete_document method
        success = DataAugmentationModel.delete_document(document_id, tenant_id)

        if success:
            flash('Document removed successfully!', 'success')
        else:
            flash('Failed to remove document. Please try again.', 'danger')

        return redirect(url_for('routes.data_augmentation'))

    except Exception as e:
        flash(f'An error occurred while removing the document: {str(e)}', 'danger')
        return redirect(url_for('routes.data_augmentation'))
        
        
@routes.route('/add_url', methods=['POST'])
def add_url():
    print("URL Link Testing")
    try:
        tenant_id = session.get('tenant_id')  # Get tenant ID from session
        if request.method == 'POST':
            # Accessing form inputs
            #urllink = request.form.get('url-input')  # Get URL from form input
            Urls = request.form.get('url')  # This might be for some other purpose
 

            # Check if the URL is provided
            if not Urls:
                flash('No URL provided.', 'danger')
                 

            # Call the model's function to add the URL to the database
            message = DataAugmentationModel.add_url_if_not_exists(Urls, "Uploaded", tenant_id)

            # Return the response message
            return message

        return flash('No URL added.', 'danger')

    except Exception as e:
        return flash(f'An error occurred: {str(e)}', 'danger')  


@routes.route('/remove_url', methods=['POST'])
def remove_url():
    try:
        print(f"Remove URL")
        url_id = request.form.get('url_id')  # Get the URL ID from the form
        tenant_id = session.get('tenant_id')  # Get the tenant ID from the session

        # Call the delete_url method from your model (you need to define this method)
        success = DataAugmentationModel.delete_url(url_id, tenant_id)

        if success:
            flash('URL removed successfully!', 'success')
        else:
            flash('Failed to remove URL. Please try again.', 'danger')

        return redirect(url_for('routes.data_augmentation'))

    except Exception as e:
        flash(f'An error occurred while removing the URL: {str(e)}', 'danger')
        return redirect(url_for('routes.data_augmentation'))
@routes.route('/add_update_databaseconnection', methods=[  'POST'])
def add_update_databaseconnection():
    try:
        tenant_id = session.get('tenant_id')  # Get tenant ID from session
        
        if request.method == 'POST':
            # Get database connection details from form inputs
            hostname = request.form.get('hostname')
            port = request.form.get('port')
            databasename = request.form.get('databasename')
            username = request.form.get('username')
            password = request.form.get('password')

            print(f"hostname: {hostname}")
            print(f"port: {port}")
            print(f"databasename: {databasename}")
            print(f"username: {username}")
            print(f"password: {password}")

            # Call the new function to add or update the database connection
            db_id = DataAugmentationModel.upsert_db_connection(
                hostname=str(hostname),
                databasename=str(databasename),
                username=username,
                password=password,
                db_status="Uploaded",
                tenant_id=tenant_id,
                port=str(port)
            )

            if db_id:  # Check if the database connection was added/updated successfully
                flash(  'Database connection details saved successfully!', 'success')
            else:
                flash( 'Failed to save database connection.', 'danger')
        else:
            flash('No database connection details provided.', 'danger')

    except Exception as e:
        flash( f'An error occurred: {str(e)}', 'danger')
    return redirect(url_for('routes.data_augmentation'))
    

@routes.route('/data_augmentation', methods=['GET'])
def data_augmentation():
    tenant_id = session.get('tenant_id')
    try:
        # Retrieve data to render in the template
        documents = DataAugmentationModel.get_all_documents(tenant_id)
        #print(f"documents {documents}")
        Urls = DataAugmentationModel.get_all_urls(tenant_id)
        print(f"URLS {Urls}")
        databaseconnection = DataAugmentationModel.get_all_db_connection(tenant_id)  
       # print(f"documents {databaseconnection}")
        # Render the template with the retrieved data
        return render_template('data_augmentation/data_augmentation.html', 
                               documents=documents, 
                               Urls=Urls, 
                               databaseconnection=databaseconnection)

    except Exception as e:
        flash('An error occurred while processing data augmentation: {}'.format(e), 'danger')
        return redirect(url_for('routes.data_augmentation'))

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
            uploads_dir = 'static/uploads/'+str(tenant_id)+'/botconfig/'
            bot_avatar_filename = bot_avatar_file.filename if bot_avatar_file else None
            if not os.path.exists(uploads_dir):
                    os.makedirs(uploads_dir)     
            bot_avatar_filepath  =""
            if bot_avatar_file:                        
                bot_avatar_filepath = os.path.join(uploads_dir, bot_avatar_filename)
                bot_avatar_file.save(bot_avatar_filepath)   
            # Handle workspace background file upload
            workspace_bg_file = request.files.get('input_workspace_background')
            workspace_bg_filename = workspace_bg_file.filename if workspace_bg_file else None
            workspace_bg_filepath=""
            if workspace_bg_file:
                workspace_bg_filepath = os.path.join(uploads_dir, workspace_bg_filename)
                workspace_bg_file.save(workspace_bg_filepath)
            print(f"workspace_bg_filename = {workspace_bg_filename}")

            # Pass form values directly to the update function
            updated = BotConfigurationModel.update_configuration(
                
                tenant_id=tenant_id,
                model_name=request.form.get('input_model_name'),
                model_key=request.form.get('input_model_key'),
                creativity=float(request.form.get('input_creativity', 0.1)),
                threshold=float(request.form.get('input_threshold', 0.1)),
                bot_name=request.form.get('input_bot_name'),
                bot_avatar=bot_avatar_filepath,
                bot_workspace=workspace_bg_filepath,
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
    
 


@routes.route('/training', methods=['GET', 'POST'])
def training():
    try:
        tenant_id = session.get('tenant_id')
        
        if request.method == 'POST':
            # Handle POST request for adding/updating training configuration
            chunking_type = request.form.get('chunking_type')
            full_retrain_or_only_remaining = request.form.get('full_retrain_or_only_remaining')
            chunk_size = int(request.form.get('chunk_size'))
            overlap = int(request.form.get('overlap'))
            search_type = request.form.get('search_type')

     
            training_id = TrainingModel.upsert_training(
                tenant_id, 
                chunking_type, 
                full_retrain_or_only_remaining, 
                chunk_size, 
                overlap, 
                search_type
            )

            if training_id is not None:
                flash('Training configuration saved successfully, and training has started!', 'success')

                return redirect(url_for('routes.training'))  # Redirect after successful POST

            flash('Failed to save training configuration.', 'danger')
        
        # Handle GET request
        trainingdata = TrainingModel.get_training_configuration(tenant_id)  # Fetch all training data for the tenant
        print(f" trainingdata {trainingdata} ")
        return render_template('training/training_setting.html', trainingdata=trainingdata)
    
    except Exception as e:
        flash('An error occurred while loading the training page: {}'.format(e), 'danger')
        return redirect(url_for('routes.training'))


@routes.route('/start_training', methods=['POST'])
def start_training():
    try:
        # Placeholder for the training logic
        # For example, you could call a function to start training here
        pass
        
        # Flash a success message after the training starts
        flash('Training started successfully!', 'success')
    except Exception as e:
        # Flash an error message if an exception occurs
        flash('An error occurred while starting the training: {}'.format(e), 'danger')
    
    # Redirect to the training configuration page or wherever appropriate
    return redirect(url_for('routes.training'))  # Adjust this if needed
 
    
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
