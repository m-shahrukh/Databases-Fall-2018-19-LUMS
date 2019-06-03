

CREATE TABLE  `BLOOD_BANK` 
   (  `BANK_ID` INT NOT NULL, 
  `ADDRESS` VARCHAR(200) NOT NULL, 
  `CITY` VARCHAR(30) NOT NULL, 
  `A+` INT NOT NULL, 
  `A-` INT NOT NULL, 
  `B+` INT NOT NULL, 
  `B-` INT NOT NULL, 
  `AB+` INT NOT NULL, 
  `AB-` INT NOT NULL, 
  `O+` INT NOT NULL, 
  `O-` INT NOT NULL, 
   CONSTRAINT `PK_BLOODBANK` PRIMARY KEY (`BANK_ID`) 
   );

CREATE TABLE  `BLOOD_DONOR` 
   (  `DONOR_ID` INT NOT NULL, 
  `FULL_NAME` VARCHAR(40) NOT NULL, 
  `GENDER` VARCHAR(10) NOT NULL, 
  `WEIGHT` INT NOT NULL, 
  `BLOOD_TYPE` VARCHAR(3) NOT NULL, 
  `DATEOFBIRTH` DATE NOT NULL, 
   CONSTRAINT `PK_BLOODDONOR` PRIMARY KEY (`DONOR_ID`) 
   );

create table Donor_Email(
  Donor_ID    INT NOT NULL,
  Email  varchar(50),
  constraint fk_donorbank2 foreign key (Donor_ID) references Blood_Donor (Donor_ID)
  ON DELETE CASCADE
);

create table Donor_Address(
  Donor_ID    INT not null,
  Address  VARCHAR(200) not null,
  constraint fk_donorbank3 foreign key (Donor_ID) references Blood_Donor (Donor_ID)
  ON DELETE CASCADE
);

create table Donor_Contact(
  Donor_ID    INT NOT NULL,
  Contact  VARCHAR(20),
  constraint fk_donorbank4 foreign key (Donor_ID) references Blood_Donor (Donor_ID)
  ON DELETE CASCADE
);

create table Diseases(
  Disease_ID  INT NOT NULL,
  Disease_Name  VARCHAR(40) not null,
  constraint pk_dieases primary key (Disease_ID)
);

create table Donor_Diseases(
  Donor_ID    INT NOT NULL,
  Disease_ID  INT,
  constraint fk_donorbank1 foreign key (Donor_ID) references Blood_Donor (Donor_ID)
  ON DELETE CASCADE,
  constraint fk_disease foreign key (Disease_ID) references Diseases (Disease_ID)
  ON DELETE CASCADE
);

create table Donor_Bank(
  Donor_ID    INT NOT NULL,
  Bank_ID  INT,
  constraint fk_donorbank5 foreign key (Donor_ID) references Blood_Donor (Donor_ID)
  ON DELETE CASCADE,
  constraint fk_donorbank6 foreign key (Bank_ID) references Blood_Bank (Bank_ID)
  ON DELETE CASCADE
);

create table Blood_Drive(
  Drive_ID    INT NOT NULL,
  Bank_ID    INT not null,
  Location     VARCHAR(200) not null,
  Starting_date date not null,
  ending_date date not null,
  constraint pk_blooddrive primary key (Drive_ID),
  constraint fk_bloodbank foreign key (Bank_ID) references Blood_Bank (Bank_ID)
  ON DELETE CASCADE
);

create table Blood_Drive_Donor(
  Drive_Donor_ID    INT NOT NULL,
  Drive_ID    INT not null,
  Full_Name    VARCHAR(40) not null,
  Gender      VARCHAR(10) not null,
  DateOfBirth     date not null,
  Blood_Type    VARCHAR(3) not null,
  Donation_date date not null,
  constraint pk_blooddrivedonor primary key (Drive_Donor_ID),
  constraint fk_blooddrive1 foreign key (Drive_ID) references Blood_Drive (Drive_ID)
  ON DELETE CASCADE
);



create table Blood_Acceptor(
  Acceptor_ID    INT NOT NULL,
  Full_Name    VARCHAR(40) not null,
  Gender      VARCHAR(10) not null,
  Weight      INT not null,
  DateOfBirth      date not null,
  Blood_Type    VARCHAR(3) not null,
  constraint pk_bloodacceptor primary key (Acceptor_ID)
);

create table Acceptor_Bank(
  Acceptor_ID INT NOT NULL,
  Bank_ID  INT,
  constraint fk_acceptorbank foreign key (Bank_ID) references Blood_Bank (Bank_ID)
  ON DELETE CASCADE,
  constraint fk_acceptorbank1 foreign key (Acceptor_ID) references Blood_Acceptor (Acceptor_ID)
  ON DELETE CASCADE
);

create table Acceptor_Email(
  Acceptor_ID    INT NOT NULL,
  Email  VARCHAR(50),
  constraint fk_bloodacceptor1 foreign key (Acceptor_ID) references Blood_Acceptor (Acceptor_ID)
  ON DELETE CASCADE
);

create table Acceptor_Address(
  Acceptor_ID    INT NOT NULL,
  Address  VARCHAR(200) not null,
  constraint fk_bloodacceptor2 foreign key (Acceptor_ID) references Blood_Acceptor (Acceptor_ID)
  ON DELETE CASCADE
);

create table Acceptor_Contact(
  Acceptor_ID    INT NOT NULL,
  Contact  VARCHAR(20),
  constraint fk_bloodacceptor3 foreign key (Acceptor_ID) references Blood_Acceptor (Acceptor_ID)
  ON DELETE CASCADE
);

create table Blood_Issued(
  Issue_ID    INT NOT NULL,
  Donor_ID   INT not null,
  Acceptor_ID  INT not null,
  constraint pk_bloodissue primary key (Issue_ID),
  constraint fk_bloodissue2 foreign key (Acceptor_ID) references Blood_Acceptor (Acceptor_ID)
  ON DELETE CASCADE
);

create table Blood_Sample(
  Sample_ID    INT NOT NULL,
  Donor_ID    INT not null,
  constraint pk_bloodsample primary key (Sample_ID),
  constraint fk_blooddonor2 foreign key (Donor_ID) references Blood_Donor (Donor_ID)
  ON DELETE CASCADE
);

create table Issued_Dates(
  Issue_ID    INT not null,
  DateOfIssue   date not null,
  constraint fk_bloodissue3 foreign key (Issue_ID) references Blood_Issued (Issue_ID)
  ON DELETE CASCADE
);

create table Pending_Requests(
  Request_ID    INT NOT NULL,
  Acceboptor_ID   INT not null,
  DateOfRequest  date not null,
  constraint pk_request primary key (Request_ID),
  constraint fk_request1 foreign key (Acceptor_ID) references Blood_Acceptor (Acceptor_ID)
  ON DELETE CASCADE
);

create table Acceptor_Diseases(
  Acceptor_ID    INT NOT NULL,
  Disease_ID  INT,
  constraint fk_donorbank7 foreign key (Acceptor_ID) references Blood_acceptor (acceptor_ID)
  ON DELETE CASCADE,
  constraint fk_disease1 foreign key (Disease_ID) references Diseases (Disease_ID)
  ON DELETE CASCADE
);

create table Sample_Dates(
  Sample_ID    INT not null,
  Date_of_sample   date not null,
  constraint fk_bloodsample3 foreign key (sample_ID) references Blood_sample (sample_ID)
  ON DELETE CASCADE
);

