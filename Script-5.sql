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


--tabla productos
create table product (
	id_producto integer primary key,
	precUnidad decimal,
	nombreProduc varchar(50) not null,
	id_empresa integer,
	CONSTRAINT fk_empresa
      FOREIGN KEY(id_empresa) 
	  REFERENCES supplier(id_empresa)	
);
alter table product add column cantidad integer;


--tabla pedidos
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


--nueva tabla pacientes
CREATE TABLE pacientes (
    nombre     varchar(15),
    apellido1  varchar(20),
    apellido2  varchar(20),
    DNI        varchar(9) primary key,
    ID_cita    INTEGER
);

drop table pacientes;
select * from pacientes;


--nueva tabla citas
create table cita(
	id_cita		integer primary key ,
	id_paciente	varchar(9),
	id_user		integer,
	fecha		date,
	descripcion	varchar(255),
	constraint fk_usuario
    	foreign key (id_user)
    	references Users(id_user),
    constraint fk_paciente
    	foreign key (id_paciente)
    	references pacientes(DNI)
);

alter table employees add constraint fk_userid foreign key(emp_user_id) references users(id_user);


---insertar datos
INSERT INTO Users (id_user, username, user_password, image_profile) VALUES
(1, 'JuanPerez', 'contraseña123','Admin'),
(2, 'MariaGarcia', 'clave456', 'Dentista'),
(3, 'PedroLopez', 'pass789', 'Recepcionista'),
(123, 'John', 'contraseña123','Admin'),
(456, 'Jane', 'clave456', 'Dentista'),
(789, 'Michael', 'pass789', 'Recepcionista')
;

INSERT INTO Users (id_user, username, user_password, image_profile) VALUES
(123, 'John', 'contraseña123','Admin'),
(456, 'Jane', 'clave456', 'Dentista'),
(789, 'Michael', 'pass789', 'Recepcionista');
INSERT INTO Users (id_user, username, user_password, image_profile) VALUES
(4, 'Armando', 'pass789', 'Admin');



INSERT INTO supplier (id_empresa, nombre_empresa) VALUES
(1, 'Dentistas Martínez'),
(2, 'Clínica Dental García'),
(3, 'Consultorio Dental López');


--productos usados
INSERT INTO product (id_producto, precUnidad, nombreProduc, id_empresa) VALUES
(1, 50.00, 'Blanqueamiento Dental', 1),
(2, 150.00, 'Limpieza Dental Profunda', 2),
(3, 80.00, 'Extracción de Muela', 3);


--pedidos usados
INSERT INTO pedidos (id_pedido, id_usuario, id_producto, cantidad, fecha, precioTotalUnidad, id_empresa) VALUES
(1, 1, 1, 23, '2023-05-08', 50.00, 1),
(2, 2, 2, 45, '2023-05-09', 300.00, 2),
(3, 3, 3, 32, '2023-05-10', 80.00, 3);




 --pacientes y citas creados
INSERT INTO pacientes (nombre, apellido1, apellido2, DNI, ID_cita)
VALUES 
  ('Juan', 'García', 'López', '12345678A', 1),
  ('María', 'Martínez', 'Sánchez', '98765432B', 2),
  ('Pedro', 'Fernández', 'Gómez', '56789012C', 3);

INSERT INTO cita (id_cita, id_paciente, id_user, fecha, descripcion)
VALUES
  (1, '12345678A', 1, '2023-05-01', 'Cita de rutina'),
  (2, '98765432B', 2, '2023-05-02', 'Extracción dental'),
  (3, '56789012C', 3, '2023-05-03', 'Limpieza dental'),
  (4, '12345678A', 123, '2023-05-04', 'Consulta de ortodoncia'),
  (5, '98765432B', 456, '2023-05-05', 'Tratamiento de conducto');
 

 
 --query para realizar la consulta en python
 SELECT c.id_cita,c.fecha, c.descripcion,p.dni,p.nombre,p.apellido1  
 					from pacientes p join cita c on p.dni=c.id_paciente order by fecha;
 
--p.dni,p.nombre,p.apellido1,p.apellido2, p.id_cita 
select * from cita;

 


