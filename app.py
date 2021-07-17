from flask import Flask, redirect, render_template, request, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, UserMixin, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from flask_mail import Mail, Message
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'arrozcomatum'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workflowauto.db'
bcrypt = Bcrypt(app)


##########################################
#             BASE DE DADOS              # 
##########################################
today = date.today()
tempo_inicio = time.time()

db = SQLAlchemy(app)
#db.create_all()
#Clients.query.all()

class Clients(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	nome = db.Column(db.String(100), nullable = False)
	morada = db.Column(db.String(500), nullable = False, default="Nao inserido")
	cc = db.Column(db.String(10), nullable = False, default="Nao inserido")
	nif = db.Column(db.String(20), nullable = False, default="Nao inserido", unique=True)
	telefone = db.Column(db.Integer, nullable = False, default="Nao inserido", unique=True)
	email = db.Column(db.String(100), nullable = False, default="Nao inserido", unique=True)
	data_registo = db.Column(db.String(20), nullable =False, default=today.strftime("%d/%m/%Y"))
	#oficina = db.Column(db.Integer, db.ForeignKey('oficina.id'), nullable = False) Não é necessario

	def __repr__(self):
		return 'Cliente ' + str(self.id)

class users(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key = True)
	nome = db.Column(db.String(100), nullable = False)
	morada = db.Column(db.String(500), nullable = False, default = "Nao inserido")
	cc = db.Column(db.String(10), nullable = False, default = "Nao inserido", unique=True)
	cargo = db.Column(db.String(20), nullable=False, default = "Patrao")
	#oficina =  db.Column(db.String(10), nullable=False, default = "Sem oficina") Não é necessario
	nif = db.Column(db.String(20), nullable = False, default = "Nao inserido", unique=True)
	telefone = db.Column(db.Integer, nullable = False, default = "Nao inserido", unique=True)
	email = db.Column(db.String(100), nullable = False, default ="Nao inserido", unique=True)
	password = db.Column(db.String(100), nullable = False, default ="ola")
	data_registo = db.Column(db.String(20), nullable =False, default = today.strftime("%d/%m/%Y") )

	def __repr__(self):
		return 'Utilizador ' + str(self.id)

class Oficina(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	nome = db.Column(db.String(100), nullable = False, default = "Nao inserido")
	morada = db.Column(db.String(500), nullable = False, default = "Nao inserido")
	descricao = db.Column(db.String(100), nullable = False, default = "Sem descricao")
	email = db.Column(db.String(500), nullable = False, default = "Nao inserido")
	telefone = db.Column(db.Integer, nullable = False, default = "Nao inserido", unique=True)
	dono = db.Column(db.Integer, nullable = False, default = "Nao inserido", unique=True)
	data_registo = db.Column(db.String(20), nullable =False, default = today.strftime("%d/%m/%Y") )

	def __repr__(self):
		return 'Oficina ' + str(self.id)

class Veiculo(db.Model):
	id = db.Column(db.Integer, primary_key = True, unique = True)
	dono = db.Column(db.Integer, nullable = False)
	marca = db.Column(db.String(50), nullable = False)
	modelo = db.Column(db.String(50), nullable = False)
	matricula = db.Column(db.String(9), nullable = False, unique=True)
	mes_ano = db.Column(db.String(8), nullable = False)
	num_chassi = db.Column(db.String(100), nullable = False, unique=True)
	combustivel = db.Column(db.String(10), nullable = False)
	potencia = db.Column(db.String(10), nullable = False, default = "Nao inserido")
	transmissao = db.Column(db.String(20), nullable = False, default = "Nao inserido")
	cilindrada = db.Column(db.String(10), nullable = False, default = "Nao inserido")
	tipo = db.Column(db.String(30), nullable = False, default = "Nao inserido")
	plataforma = db.Column(db.String(20), nullable = False, default = "Nao inserido")
	data_registo = db.Column(db.String(20), nullable =False, default= today.strftime("%d/%m/%Y") )
	#estado = db.Column(db.String(20), nullable = False, default = "Composto")

	def __repr__(self):
		return 'Veiculo ' + str(self.id)



class reparacoes(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	cliente = db.Column(db.Integer, nullable = False)
	veiculo = db.Column(db.Integer, nullable = False)
	mecanico = db.Column(db.Integer, nullable = False)
	dataInicio = db.Column(db.String(20), nullable = False, default = today.strftime("%d/%m/%Y") )
	dataFim = db.Column(db.String(20), nullable =False, default = today.strftime("%d/%m/%Y") )
	tempoInicio = db.Column(db.Float, nullable = False, default = 0)
	tempoFim = db.Column(db.Float, nullable = False, default = 0)
	avaria = db.Column(db.String(500), nullable = False)
	feito = db.Column(db.String(500), nullable = False)
	diagnostico = db.Column(db.String(500), nullable = False)
	estado = db.Column(db.String(500), nullable = False, default = "Concluida")

	def __repr__(self):
		return 'Reparacao ' + str(self.id)


######################################
#             Redirects              #
######################################

#########
# Geral #
#########


@app.route("/")
def index():
	oficina = Oficina.query.first()
	if current_user.is_authenticated:
		return redirect("/admindashboard")

	return render_template("Geral/index.html",oficina = oficina)


@app.route("/clientdashboard")
def clientdashboard():

	return render_template("Geral/index.html")


##############
## Software ##
##############
#Verificar se o utilizador e cliente ou nao
def verificaCliente(cargo):
	if cargo == "cliente":
		return redirect("/clientdashboard")

#Página Contactos
@app.route("/contactos")
def contacts():

	oficina = Oficina.query.first()
	return render_template("Geral/contact.html", oficina = oficina)


#Home
@app.route("/admindashboard")
@login_required
def admindashboard():

	numClients = Clients.query.count()
	numReps = reparacoes.query.count()
	numVei = Veiculo.query.count()
	numFunc = users.query.filter(users.cargo != 'Patrao').count()



	return render_template("Software/index.html", numClients = numClients, numReps = numReps, numVei = numVei, numFunc = numFunc)


#Perfil Veiculo
@app.route("/admindashboard/veiculo/<id>")
@login_required
def carprofile(id):

	veiculo = Veiculo.query.filter(Veiculo.id == id).first()

	reps = reparacoes.query.filter(reparacoes.veiculo == id)

	dono = Clients.query.filter(Clients.id == veiculo.dono).first()

	if veiculo:

		return render_template("Software/pages/examples/carprofile.html", veiculo = veiculo, reps = reps, dono = dono)

	else:

		return render_template("Software/pages/examples/404.html")


#Perfil Cliente
@app.route("/admindashboard/client/<id>")
@login_required
def clientprofile(id):

	cliente = Clients.query.filter(Clients.id == id).first()

	veiculos = Veiculo.query.filter(Veiculo.dono == id)

	if cliente:

		return render_template("Software/pages/examples/clientprofile.html", cliente = cliente, veiculos = veiculos)

	else:

		return render_template("Software/pages/examples/404.html")


#Perfil Funcionario
@app.route("/admindashboard/func/<id>")
@login_required
def funcprofile(id):

	func = users.query.filter(users.id == id).first()


	if func:

		return render_template("Software/pages/examples/funcprofile.html", func = func)

	else:

		return render_template("Software/pages/examples/404.html")


#Detalhes Reparacoes
@app.route("/admindashboard/repdetails/<id>", methods=['GET','POST'])
@login_required
def repdetails(id):

	rep = reparacoes.query.filter(reparacoes.id == id).first()

	oficina = Oficina.query.filter(Oficina.id == 1).first()

	data = today.strftime("%d/%m/%Y")

	if rep:



		cliente = Clients.query.filter(Clients.id == rep.cliente).first()

		veiculo = Veiculo.query.filter(Veiculo.id == rep.veiculo).first()

		mecanico = users.query.filter(users.id == rep.mecanico).first()

		if rep.estado == "Concluida":

			return render_template("Software/pages/examples/repsConcluidasDetails.html", rep = rep, cliente = cliente, data = data, veiculo = veiculo, mecanico = mecanico, oficina = oficina)

		else:

			if request.method == "POST":

				avaria = request.form['avaria']
				feito = request.form['feito']
				diagnostico = request.form['diagnostico']
				dataFim = data
				estado = "Concluida"

				if rep.estado == "Aberta":

					tmp_agora = time.time()

					tmp_inicio = rep.tempoFim

					registarTempo = (tmp_agora - tmp_inicio) / 3600
					tmp_formatado = round(registarTempo, 2)

				else:

					tmp_fim = time.time()
					tmp_registar = rep.tempoInicio / 3600
					tmp_formatado = round(tmp_registar, 2)

				try:
					num_rows_updated = reparacoes.query.filter(reparacoes.id == id).update(dict(diagnostico = diagnostico, avaria = avaria, feito = feito, estado = estado, dataFim = dataFim, tempoInicio = tmp_formatado))
					db.session.commit()
					flash('Reparação concluida com sucesso.','success')
					return redirect("/admindashboard/listreps")

				except:
					flash('Houve um problema ao concluir a reparação.','danger')
					return redirect("/admindashboard/listreps")

			return render_template("Software/pages/examples/repsAbertsDetails.html", rep = rep, cliente = cliente, data = data, veiculo = veiculo)

	else:

		return render_template("Software/pages/examples/404.html")



#Detalhes Reparacoes
@app.route("/admindashboard/repdetails/print/<id>")
@login_required
def repPrint(id):

	rep = reparacoes.query.filter(reparacoes.id == id).first()

	oficina = Oficina.query.filter(Oficina.id == 1).first()
	
	data = today.strftime("%d/%m/%Y")

	if rep:

		cliente = Clients.query.filter(Clients.id == rep.cliente).first()

		veiculo = Veiculo.query.filter(Veiculo.id == rep.veiculo).first()

		mecanico = users.query.filter(users.id == rep.mecanico).first()

		return render_template("Software/pages/examples/rep-print.html", oficina = oficina, rep = rep, cliente = cliente, data = data, veiculo = veiculo, mecanico = mecanico)

	else:

		return render_template("Software/pages/examples/404.html")



#Apagar cliente
@app.route("/delete/client/<id>")
@login_required
def clientdelete(id):

	cliente_to_delete = Clients.query.get_or_404(id)

	try:
		db.session.delete(cliente_to_delete)
		Veiculo.query.filter(Veiculo.dono == id).delete()
		reparacoes.query.filter(reparacoes.cliente == id).delete()
		db.session.commit()
		flash('Cliente apagado com sucesso.','success')
		return redirect("/admindashboard/listclients")

	except:
		flash('Houve um problema ao apagar o cliente.','danger')
		return redirect("/admindashboard/listclients")

	

#Apagar funcionario
@app.route("/delete/func/<id>")
@login_required
def funcdelete(id):

	func_to_delete = users.query.get_or_404(id)

	try:
		db.session.delete(func_to_delete)
		db.session.commit()
		flash('Funcionário apagado com sucesso.','success')
		return redirect("/admindashboard/listafunc")

	except:
		flash('Houve um problema ao apagar o funcionário.','danger')
		return redirect("/admindashboard/listafunc")


#Apagar veiculo
@app.route("/delete/veiculo/<id>")
@login_required
def veidelete(id):

	veiculo_to_delete = Veiculo.query.get_or_404(id)

	profile_to_redirect = Veiculo.query.filter(Veiculo.dono == id).first()
	try:
		reparacoes.query.filter(reparacoes.veiculo == id).delete()
		db.session.delete(veiculo_to_delete)
		db.session.commit()
		flash('Veiculo apagado com sucesso.','success')
		return redirect("/admindashboard/listclients")

	except:
		flash('Houve um problema ao apagar o veiculo.','danger')
		return redirect("/admindashboard/listclients")

	#return render_template("Software/pages/examples/clientprofile.html", cliente = cliente)


#Apagar reparacao
@app.route("/delete/rep/<id>")
@login_required
def repdelete(id):

	rep_to_delete = reparacoes.query.get_or_404(id)

	try:
		db.session.delete(rep_to_delete)
		db.session.commit()
		flash('Reparação apagada com sucesso.','success')
		return redirect("/admindashboard/listreps")

	except:
		flash('Houve um problema a apagar a reparação.','danger')
		return redirect("/admindashboard/listreps")

	#return render_template("Software/pages/examples/clientprofile.html")


#Pausar reparacao
@app.route("/pause/rep/<id>")
@login_required
def reppause(id):

	rep_to_pause = reparacoes.query.get_or_404(id)

	registarTempo = ((time.time() - rep_to_pause.tempoFim) + rep_to_pause.tempoInicio)
	#registarTempo = registarTempo/60
	registarTempo = '{:.2f}'.format(registarTempo)

	try:
		num_rows_updated = reparacoes.query.filter(reparacoes.id == id).update(dict(estado = "Pausa", tempoInicio = registarTempo))
		db.session.commit()
		flash('Reparação em pausa.','success')
		return redirect("/admindashboard/listreps")

	except:
		flash('Houve um problema a colocar a reparação em pausa.','danger')
		return redirect("/admindashboard/listreps")

	#return render_template("Software/pages/examples/clientprofile.html")

@app.route("/return/rep/<id>")
@login_required
def repreturn(id):

	rep_to_return = reparacoes.query.get_or_404(id)

	tmp_registar = time.time()

	try:
		num_rows_updated = reparacoes.query.filter(reparacoes.id == id).update(dict(estado = "Retomada", tempoFim = tmp_registar))
		db.session.commit()
		flash('Reparação retomada.','success')
		return redirect("/admindashboard/listreps")

	except:
		flash('Houve um problema a colocar a reparação em pausa.','danger')
		return redirect("/admindashboard/listreps")

	#return render_template("Software/pages/examples/clientprofile.html")

############
# Registos #
############

#Register Client Car
@app.route("/admindashboard/addcar", methods=['GET','POST'])
@login_required
def addcar():
	if request.method == "POST":

		marca = request.form['marca']
		modelo = request.form['modelo']
		matricula = request.form['matricula']
		mesano = request.form['mesano']
		nchassi = request.form['nchassi']
		combustivel = request.form['combustivel']
		potencia = request.form['potencia']
		cilindrada = request.form['cilindrada']
		caixa = request.form['caixa']
		tipo = request.form['tipo']
		plataforma = request.form['plataforma']
		dono = request.form['dono']


		checkmatricula = db.session.query(Veiculo.query.filter(Veiculo.matricula == matricula).exists()).scalar()
		checkchassi = db.session.query(Veiculo.query.filter(Veiculo.num_chassi == nchassi).exists()).scalar()

		if not checkmatricula and not checkchassi:
			new_register = Veiculo(dono = dono,  marca = marca, modelo = modelo, matricula = matricula, mes_ano = mesano, num_chassi = nchassi, combustivel = combustivel, potencia  = potencia , transmissao  = caixa, cilindrada  = cilindrada , tipo  = tipo , plataforma  = plataforma )
			db.session.add(new_register)
			db.session.commit()
			flash('Veículo registado com sucesso.','success')
			return redirect("/admindashboard/addcar")

		else:

			flash('Veículo já existe.','danger')
			return redirect("/admindashboard/addcar")

	all_clients = Clients.query.all()

	return render_template("Software/pages/forms/formAddCar.html", clients=all_clients)


#Register Client
@app.route("/admindashboard/addclient", methods=['GET','POST'])
@login_required
def addclient():
	if request.method == "POST":

		nome = request.form['nome']
		cc = request.form['cc']
		nif = request.form['nif']
		morada = request.form['morada']
		telemovel = request.form['telemovel']
		email = request.form['clientemail']

		checkemail = db.session.query(Clients.query.filter(Clients.email == email).exists()).scalar()
		checkcc = db.session.query(Clients.query.filter(Clients.cc == cc).exists()).scalar()
		checknif = db.session.query(Clients.query.filter(Clients.nif == nif).exists()).scalar()
		checktelemovel = db.session.query(Clients.query.filter(Clients.telefone == telemovel).exists()).scalar()

		if not checkemail and not checkcc and not checknif and not checktelemovel:
			new_register = Clients(nome = nome,  morada = morada, cc = cc, nif = nif, telefone = telemovel, email = email )
			db.session.add(new_register)
			db.session.commit()
			flash('Cliente registado com sucesso.','success')
			return redirect("/admindashboard/addclient")

		else:
			flash('Cliente já existe.','danger')
			return redirect("/admindashboard/addclient")

	return render_template("Software/pages/forms/formAddClient.html")

#Register Rent Car
@app.route("/admindashboard/addrentcar")
@login_required
def addrentcar():
	return render_template("Software/pages/forms/formAddRentCar.html")




#Registo Reparacoes
@app.route("/admindashboard/newrepair", methods=['GET','POST'])
@login_required
def newRep():

	if request.method == "POST":
		mecanico = current_user.id
		cliente = request.form['cliente']
		avaria = request.form['avaria']
		feito = request.form['feito']
		veiculo = request.form['veiculo']
		diagnostico = request.form['diagnostico']
		estado = 'Pausa'

		try:
			new_register = reparacoes(cliente = cliente,  avaria = avaria, feito = feito, veiculo = veiculo, mecanico = mecanico, diagnostico = diagnostico, estado = estado)
			db.session.add(new_register)
			db.session.commit()
			flash('Reparação registada com sucesso.','primary')
			return redirect("/admindashboard/newrepair")

		except:
			flash('Houve um problema ao registar a reparação.','danger')
			return redirect("/admindashboard/newrepair")


	all_clients = Clients.query.all()
	veiculos = Veiculo.query.all()

	return render_template("Software/pages/forms/formNewRep.html", clients = all_clients, veiculos = veiculos)




#Registar Funcionário
@app.route("/admindashboard/addfunc", methods=['GET','POST'])
@login_required
def addfunc():
	if current_user.cargo == 'Patrao' or current_user.cargo == 'Gerente':
		if request.method == "POST":

			nome = request.form['nome']
			cc = request.form['cc']
			nif = request.form['nif']
			morada = request.form['morada']
			telemovel = request.form['telemovel']
			email = request.form['clientemail']
			pwd = request.form['pwd']
			cargo = request.form['cargo']

			checkemail = db.session.query(users.query.filter(users.email == email).exists()).scalar()
			checkcc = db.session.query(users.query.filter(users.cc == cc).exists()).scalar()
			checknif = db.session.query(users.query.filter(users.nif == nif).exists()).scalar()
			checktelemovel = db.session.query(users.query.filter(users.telefone == telemovel).exists()).scalar()
				
			if not checkemail and not checkcc and not checknif and not checktelemovel:

				hash_password = bcrypt.generate_password_hash(pwd).decode('utf-8')

				new_register = users(nome = nome,  morada = morada, cc = cc, cargo = cargo, nif = nif, telefone = telemovel, email = email, password = hash_password )
				db.session.add(new_register)
				db.session.commit()
				flash('Funcionário registado com sucesso!', 'success')
				return redirect("/admindashboard/addfunc")
				
			else:
				flash('Email em uso ou passwords incorretas!', 'danger')
				#return '<center><script>alert("Erro: Email em uso ou passwords incorretas!")</script> ' 
				return redirect("/admindashboard/register")

		return render_template("Software/pages/forms/formAddFunc.html")
	else:

		return redirect("/admindashboard")

##########
# Listas #
##########




#List Client Car
@app.route("/admindashboard/listclientcar")
@login_required
def listClientCar():
	veiculos = Veiculo.query.all()
	dono = Clients.query.all()

	return render_template("Software/pages/tables/cliCarTable.html", veiculos = veiculos, dono = dono)






#List Clients
@app.route("/admindashboard/listclients")
@login_required
def listClients():

	all_clients = Clients.query.all()

	return render_template("Software/pages/tables/cliTable.html", clients=all_clients)





#List Funcionarios
@app.route("/admindashboard/listafunc")
@login_required
def listFunc():

	if current_user.cargo == 'Patrao' or current_user.cargo == 'Gerente':

		all_funcs = users.query.filter(users.cargo != 'Patrao')
		return render_template("Software/pages/tables/funcTable.html", funcs=all_funcs)

	else:

		return redirect("/admindashboard")




#List Reps
@app.route("/admindashboard/listreps")
@login_required
def listreps():

	reps_abertas = reparacoes.query.filter(reparacoes.estado != 'Concluida')
	reps_concluidas = reparacoes.query.filter(reparacoes.estado == 'Concluida')

	return render_template("Software/pages/tables/repTable.html", repabertas = reps_abertas, repconcluidas = reps_concluidas)




#Profile
@app.route("/admindashboard/profile", methods=['GET','POST'])
@login_required
def profile():

	# if request.method == "POST":
		
	# 	nome = request.form['nome']
	# 	email = request.form['email']
	# 	morada = request.form['morada']
	# 	telefone = request.form['telefone']

	 	#users.query.filter(users.id == current_user.id).update(dict(nome = nome,  morada = morada, email = email, telefone = telefone))


	return render_template("Software/pages/examples/profile.html")


#Página Dados da Oficina
@app.route("/admindashboard/oficina", methods=['GET','POST'])
@login_required
def oficina():

	if current_user.cargo == 'Patrao' or current_user.cargo == 'Gerente':
		
		oficina = Oficina.query.first()

		if request.method == "POST":

			nome = request.form['nome']
			morada = request.form['morada']
			descricao = request.form['descricao']
			telefone = request.form['telefone']
			email = request.form['email']
			dono = "Patrao"

			if oficina:
				Oficina.query.filter(Oficina.id == 1).update(dict(nome = nome,  morada = morada, descricao = descricao, telefone = telefone, email = email, dono = dono))
				
			else:
				new_register = Oficina(id = 1, nome = nome,  morada = morada, descricao = descricao, telefone = telefone, email = email, dono = dono)
				db.session.add(new_register)
			
			db.session.commit()
				
			flash('Dados guardados com sucesso!', 'success')
			return redirect("/admindashboard/oficina")
				

		return render_template("Software/pages/forms/oficina.html", oficina = oficina)

	else:

		return redirect("/admindashboard")



######################################
#             AUTENTICACAO           #
######################################

login_manager = LoginManager()
login_manager.login_view = '/login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
	return users.query.get(int(user_id))

#Log In
@app.route("/login", methods=['GET','POST'])
def login():
	oficina = Oficina.query.first()
	if request.method == 'POST':
		
		email = request.form['usr_email']
		password = request.form['usr_pwd']
		#remember = True if request.form['remember'] else False

		user = users.query.filter_by(email=email).first()

		if not user or not bcrypt.check_password_hash(user.password, password):
			flash('Verifique as suas credenciais.')
			return redirect("/login")

		login_user(user) #login_user(user, remember=remember)
		return redirect("/admindashboard")
		
	return render_template("Software/pages/examples/login.html", oficina=oficina)



#Log Out
@app.route("/admindashboard/logout")
@login_required
def logout():
	logout_user()
	return redirect("/")



#Register Account
@app.route("/register", methods=['GET','POST'])
def register():
	oficina = Oficina.query.first()
	exists = db.session.query(users.query.filter(users.id == 1).exists()).scalar()

	if exists:
		return redirect("/")
	else:

		if request.method == 'POST':

			nome = request.form['usr_username']
			email = request.form['usr_email']
			password = request.form['usr_pwd']
			passwordconf = request.form['usr_repwd']
			

			checkemail = db.session.query(users.query.filter(users.email == email).exists()).scalar() #Verifica se email existe na base de dados [FALSO]

			if checkemail == False and password == passwordconf:

				hash_password = bcrypt.generate_password_hash(password).decode('utf-8')

				new_register = users(nome = nome, email = email, password = hash_password)
				#new_oficina = oficina()
				db.session.add(new_register)
				#db.session.add(new_oficina)
				db.session.commit()
				return redirect("/login")
				
			else:
				flash('Email em uso ou passwords incorretas!')
				#return '<center><script>alert("Erro: Email em uso ou passwords incorretas!")</script> ' 
				return redirect("/register")

		return render_template("Software/pages/examples/register.html", oficina=oficina)



######################################
#             Start App              #
######################################

if __name__ == "__main__":
	app.run(debug=True)


#Criado por Tomas Neto 2020