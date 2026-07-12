from flask import Flask, render_template

app = Flask(__name__)

# Route for the main project overview
@app.route('/')
def index():
    return render_template('index.html')

# Route for the dedicated Tableau Dashboard page
@app.route('/dashboard')
def dashboard():
    # Replace the 'tableau_url' with your actual Tableau public/server URL
    tableau_url = "https://public.tableau.com/views/YourDashboardName/Dashboard1"
    return render_template('dashboard.html', tableau_url=tableau_url)

if __name__ == '__main__':
    # Run the application
    app.run(debug=True)