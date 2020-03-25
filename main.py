from flask import Flask, render_template, redirect, request, abort, url_for
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField, BooleanField, TextAreaField
from wtforms.validators import DataRequired
from data import db_session
from data.users import *
from flask_login import LoginManager, login_user, login_required, logout_user, current_user


app = Flask(__name__)
app.config["SECRET_KEY"] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    surname = StringField("Surname", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    age = StringField("Age", validators=[DataRequired()])
    position = StringField("Work")
    speciality = StringField("Speciality")
    address = StringField("Address")
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Create")


class LoginForm(FlaskForm):
    email = StringField("Login", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me?")
    submit = SubmitField("Enter")


class AddJob(FlaskForm):
    title = StringField("Job Title", validators=[DataRequired()])
    team_leader = StringField("Team Leader id", validators=[DataRequired()])
    work_size = StringField("Work Size", validators=[DataRequired()])
    collaborators = StringField("Collaborators", validators=[DataRequired()])
    hazard_category = StringField("Hazard category", validators=[DataRequired()])
    is_finished = BooleanField("Is job finished")
    submit = SubmitField("Submit")


class AddDepartment(FlaskForm):
    title = StringField("Department Title", validators=[DataRequired()])
    chief = StringField("Chief id", validators=[DataRequired()])
    members = StringField("Members", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route('/')
def index():
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    users = []
    for user in session.query(User).all():
        users.append(f"{user.name} {user.surname}")
    return render_template('index.html', title=f"Jobs", current_user=current_user,
                           jobs=jobs, users=users,
                           style_file=url_for('static', filename='css/style.css'))


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', form=form, title="Log in", current_user=current_user,
                               message="Wrong login or password")
    return render_template('login.html', form=form, title="Log in", current_user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('index.html', title='Log in', form=form,
                                   message='This email has already used by another user')
        user = User()
        user.surname = form.surname.data
        user.name = form.name.data
        user.age = int(form.age.data)
        user.position = form.position.data
        user.speciality = form.speciality.data
        user.address = form.address.data
        user.email = form.email.data
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        login_user(user, remember=True)
        return redirect('/')
    return render_template('register.html', form=form, title='Registration')


@app.route('/add_job', methods=["GET", "POST"])
@login_required
def add_job():
    form = AddJob()
    if form.validate_on_submit():
        session = db_session.create_session()
        try:
            job = Jobs(
                team_leader=int(form.team_leader.data),
                job=form.title.data,
                work_size=int(form.work_size.data),
                collaborators=form.collaborators.data,
                hazard_category=int(form.hazard_category.data),
                is_finished=form.is_finished.data
            )
            session.add(job)
            session.commit()
        except Exception:
            return render_template('add_job.html', title='Adding job', form=form,
                                   message="This email has already used")
        return redirect('/')
    return render_template('add_job.html', title='Adding job', form=form)


@app.route('/edit_job/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_job(id):
    form = AddJob()
    if request.method == "GET":
        session = db_session.create_session()
        jobs = session.query(Jobs).filter(Jobs.id == id,
                                          (Jobs.user == current_user) | (current_user.id == 1)).first()
        if jobs:
            form.title.data = jobs.job
            form.team_leader.data = jobs.team_leader
            form.work_size.data = jobs.work_size
            form.collaborators.data = jobs.collaborators
            form.hazard_category.data = jobs.hazard_category
            form.is_finished.data = jobs.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        jobs = session.query(Jobs).filter(Jobs.id == id,
                                          (Jobs.user == current_user) | (current_user.id == 1)).first()
        if jobs:
            jobs.job = form.title.data
            jobs.team_leader = form.team_leader.data
            jobs.work_size = form.work_size.data
            jobs.collaborators = form.collaborators.data
            jobs.hazard_category = int(form.hazard_category.data)
            jobs.is_finished = form.is_finished.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('edit_job.html', title='Editing job', form=form, id=id)


@app.route('/job_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def job_delete(id):
    session = db_session.create_session()
    jobs = session.query(Jobs).filter(Jobs.id == id,
                                      (Jobs.user == current_user) | (current_user.id == 1)).first()
    if jobs or current_user.id == 1:
        session.delete(jobs)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/departments')
def show_departments():
    session = db_session.create_session()
    departments = session.query(Departments).all()
    users = []
    for user in session.query(User).all():
        users.append(f"{user.name} {user.surname}")
    return render_template('departments.html', title=f"Departments", current_user=current_user,
                           departments=departments, users=users,
                           style_file=url_for('static', filename='css/department_style.css'))


@app.route('/add_department', methods=["GET", "POST"])
@login_required
def add_department():
    form = AddDepartment()
    if form.validate_on_submit():
        session = db_session.create_session()
        try:
            department = Departments(
                title=form.title.data,
                chief=int(form.chief.data),
                members=form.members.data,
                email=form.email.data
            )
            session.add(department)
            session.commit()
        except Exception:
            return render_template('add_department.html', title='Adding department', form=form,
                                   message="This email has already used")
        return redirect('/departments')
    return render_template('add_department.html', title='Adding department', form=form)


@app.route('/edit_department/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_department(id):
    form = AddDepartment()
    if request.method == "GET":
        session = db_session.create_session()
        departments = session.query(Departments).filter(Departments.id == id,
                                                        (Departments.user == current_user) |
                                                        (current_user.id == 1)).first()
        if departments:
            form.title.data = departments.title
            form.chief.data = departments.chief
            form.members.data = departments.members
            form.email.data = departments.email
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        departments = session.query(Departments).filter(Departments.id == id,
                                                        (Departments.user == current_user) |
                                                        (current_user.id == 1)).first()
        if departments:
            departments.title = form.title.data
            departments.chief = int(form.chief.data)
            departments.members = form.members.data
            departments.email = form.email.data
            session.commit()
            return redirect('/departments')
        else:
            abort(404)
    return render_template('edit_department.html', title='Editing department', form=form, id=id)


@app.route('/delete_department/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_department(id):
    session = db_session.create_session()
    department = session.query(Departments).filter(Departments.id == id,
                                                   (Departments.user == current_user) |
                                                   (current_user.id == 1)).first()
    if department or current_user.id == 1:
        session.delete(department)
        session.commit()
    else:
        abort(404)
    return redirect('/departments')


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


if __name__ == '__main__':
    db_session.global_init("db/jobs.sqlite")
    app.run()