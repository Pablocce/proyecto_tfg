create table Users (
	id_user integer PRIMARY KEY,
    username varchar(20) not null unique,
    user_password varchar(20) not null,
    image_profile varchar(200)
);

create table supplier (
	id_empresa integer primary key,
	nombre_empresa varchar(50) not null
);

create table product (
	id_producto integer primary key,
	precUnidad decimal,
	nombreProduc varchar(50) not null,
	id_empresa integer,
	CONSTRAINT fk_empresa
      FOREIGN KEY(id_empresa) 
	  REFERENCES supplier(id_empresa)	
);

create table pedidos(
	id_pedido integer,
	id_usuario integer,
	id_producto integer,
	cantidad integer,
	fecha date,
	precioTotalUnidad integer,
	id_empresa integer,
	primary key(id_pedido,id_usuario,id_producto),
	constraint fk_empresa1
		FOREIGN KEY(id_empresa) 
	  	REFERENCES supplier(id_empresa),
	constraint fk_user
		foreign key(id_usuario)
		references Users(id_user),
	constraint fk_producto
		foreign key(id_producto)
		references product(id_producto)
);

CREATE TABLE pacientes (
    nombre     varchar(15),
    apellido1  varchar(20),
    apellido2  varchar(20),
    DNI        varchar(9) primary key,
    ID_user    INTEGER,
    constraint fk_users
    	foreign key (id_user)
    	references Users(id_user)
);

create table cita (
	id_cita		integer(6),
	id_paciente	integer(10),
	id_user		integer(10),
	fecha		date,
	descripcion	varchar(255),
	constraint fk_usuario
    	foreign key (id_user)
    	references Users(id_user),
    constraint fk_paciente
    	foreign key (id_paciente)
    	references pacientes(DNI)
);



select * from pacientes;
update pedidos set cantidad=10 where id_pedido=3;

select *from pedidos;

---insertar datos
INSERT INTO Users (id_user, username, user_password, image_profile) VALUES
(1, 'JuanPerez', 'contraseña123','Admin'),
(2, 'MariaGarcia', 'clave456', 'Dentista'),
(3, 'PedroLopez', 'pass789', 'Recepcionista');
r
INSERT INTO supplier (id_empresa, nombre_empresa) VALUES
(1, 'Dentistas Martínez'),
(2, 'Clínica Dental García'),
(3, 'Consultorio Dental López');

INSERT INTO product (id_producto, precUnidad, nombreProduc, id_empresa) VALUES
(1, 50.00, 'Blanqueamiento Dental', 1),
(2, 150.00, 'Limpieza Dental Profunda', 2),
(3, 80.00, 'Extracción de Muela', 3);

select * from product;


INSERT INTO pedidos (id_pedido, id_usuario, id_producto, cantidad, fecha, precioTotalUnidad, id_empresa) VALUES
(1, 1, 1, 23, '2023-05-08', 50.00, 1),
(2, 2, 2, 45, '2023-05-09', 300.00, 2),
(3, 3, 3, 32, '2023-05-10', 80.00, 3);






