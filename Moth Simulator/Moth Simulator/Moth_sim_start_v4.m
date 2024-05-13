clear
clc
close all

ST=0.01; % [s] timestep della simulazione

%% Dati ambiente e andatura
rho_water=998; % kg/m3
rho_air=1.225; % kg/m3
g=9.81; % m/s2

%% Dati barca
m_sailor=75; % kg
m_hull=30; %kg
m_margin=5; %kg
m_boat=m_hull+m_margin;
m_tot=m_sailor+m_boat;
I_yy_hull=100; % kg*m2

% Posizione di tutti i punti di applicazione delle forze [tutto in metri]
% Coordinate con sdr centrato sullo specchio di poppa in basso
G_hull= [1.48 0 0.257]; 
%ca_fw= [1.81 0 -1.10];
AC_fw= [1.90 0 -1.10];
AC_rudder= [-0.56 0 -0.96];
%cm_omo= [1.10 0 0.75];
G_sailor= [0.2 0 0.75]; % La posizione 0.2 indica la posizione di inizio della terrazza, la posizione del sailor si controlla dallo slider del joystick
mast_base= [2.35 0 0.4];
AC_sail= mast_base + [-1.18 0 2.3]; %rispetto alla base dell'albero
allpt=[G_sailor;AC_fw;AC_rudder;AC_sail];

for i=1:size(allpt,1)
    allpt(i,:)=allpt(i,:)-G_hull;
end
allpt(:,3)=-1*allpt(:,3); % Il sdr body è positivo se verso il basso
%% Dati front wing
S_fw=0.09; % [m^2]
I_yy_fw=10; % [kg*m^2]

flap=[-8 -5 -2 0 3 5 8 10 12 13]';
cl_fw=[-0.35 -0.143 0.064 0.208 0.407 0.543 0.745 0.879 1.012 1.078]';
cd_fw=[0.014 0.011 0.008 0.009 0.011 0.015 0.021 0.027 0.040 0.051]';
cm_fw=[0.007 -0.025 -0.056 -0.078 -0.107 -0.127 -0.156 -0.175 -0.193 -0.202]';

funCL_fw=polyfit(flap,cl_fw,1);
funCD_fw=polyfit(flap,cd_fw,3);
funCM_fw=polyfit(flap,cm_fw,1);

%% Dati rudder
S_r=0.03946; % [m^2]
I_yy_fw=5; % [kg*m^2]

aoa=[-8 -5 -2 0 1 3 5 8 10]';
%cl_r=[-0.534 -0.257 0.026 0.197 0.282 0.452 0.621 0.872 1.037]';
cl_r=[0 0.8]';
cd_r=[0.021 0.013 0.010 0.009 0.011 0.016 0.024 0.042 0.057]';
%cm_r=-0.078; % cost perchè rispetto al CA
cm_r=0;

% funaoa_rudder=polyfit([0 aoa(end)],cl_r,1);
% funcl_r=polyval(funaoa_rudder,aoa);
% funcd_r=polyfit(cd_r,funcl_r,1);

funCL_r=polyfit([0 aoa(end)],cl_r,1);
funCD_r=polyfit(aoa,cd_r,2);
funCM_r=0;

%% Dati vela
% Si suppone che la vela venga mantenuta ad un AOA costante rispetto ad AWA
% ("se il velista è bravo"). L'AOA a cui viene mantenuta è quello di
% massima efficienza della vela, ovvero dai 4 ai 6 gradi

% Da XFLR, si calcola che la vela con un angolo dai 4 ai 6 gradi ha un CL
% medio pari a CL_sail=0.17 e un CD_sail=0.01

S_sail=8.20; % [m^2]
I_yy_sail=8; % [kg*m^2]
%CL_sail=0.20;  % Da XFLR il CL può variare da 0.15 a 0.25 a seconda della regolazione
CL_sail=0.4;  % Da XFLR il CL può variare da 0.15 a 0.25 a seconda della regolazione
CD_sail=0.05;  % Il CD di XFLR probabilmente è molto ottimistico (da CD = 0.1-0.15

%% Dati wand e camma
% L'altezza della barca dall'acqua (coordinata z) è misurata dal perno
% della wand fino al pelo dell'acqua sottostante. Per questo motivo quando
% la barca si trova a meno di circa 35-40 cm dal pelo dell'acqua si
% ipotizza fallito il volo, perchè significa che lo scafo tocca l'acqua

lower_z_limit=0.10; % [m]
wand_lenght=1.25; % [m]
wand_attach_pos=mast_base+[1.05+0.5 0 -0.1]-G_hull;

height_control=[ % Prima colonna è l'altezza z e seconda il flap angle
    0.25 10,
    0.4 8,
    0.7 6.5,
    0.8 4.5,
    0.9 3.5,
    1 2.5,
    1.1 1,
    1.15 -1,
    1.25 -2,
    1.3 -4,
];
height_control_offset=-0.35; % [m]
height_control(:,1)=height_control(:,1)+height_control_offset;

pol=polyfit(height_control(:,1),height_control(:,2),2);
flapangle=polyval(pol,linspace(0.25,1.4));
plot(linspace(0.15,1.3),flapangle);
legend('Flap angle in gradi in funzione dell altezza in metri');

%% Condizioni iniziali
I_yy_boat=I_yy_hull+I_yy_fw+I_yy_sail-50; %+m_sailor*norm(allpt(1,:))^2;

x_i=0; % [m] 
z_i=-0.25; % [m] rispetto al livello dell'acqua (il '-' perchè sdr punta verso il basso)

x_dot_i=4; % [m/s]; Velocità orizzontale iniziale della barca nel sdr inerziale (ovvero rispetto all'acqua)

mu=30; % [gradi]
mu=mu*2*pi/360;

gamma_i=-5; % [gradi]
gamma_i=gamma_i*2*pi/360;

theta_i=10; % [gradi]
theta_i=theta_i*2*pi/360;

aoa_i=gamma_i+theta_i;
aoa_i=aoa_i*360*0.5/pi;

TWS=7; % m/s
TWA=90; % gradi
TWA=TWA*2*pi/360;


%% Made by Marco Salvato
