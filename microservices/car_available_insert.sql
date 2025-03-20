Use car_service;
DROP TABLE IF EXISTS car_available;

CREATE TABLE car_available (
    id VARCHAR(13) PRIMARY KEY,
    make VARCHAR(64) NOT NULL,
    model VARCHAR(64) NOT NULL,
    year INT NOT NULL,
    color VARCHAR(64) NOT NULL,
    price_per_hour FLOAT(10,2) NOT NULL,
    available BOOLEAN DEFAULT TRUE,
    latitude DECIMAL(17,16) NOT NULL,
    longitude DECIMAL(20,17) NOT NULL
);

INSERT INTO car_available (id, make, model, year, color, price_per_hour, available, latitude, longitude) VALUES
('CAR001', 'Toyota', 'Corolla', 2023, 'Red', 35.99, TRUE, 1.37854595, 103.8394548),
('CAR002', 'Honda', 'Civic', 2022, 'Blue', 32.99, FALSE, 1.36495585, 103.843818),
('CAR003', 'Hyundai', 'Elantra', 2023, 'Green', 29.99, TRUE, 1.3720898, 103.8526935),
('CAR004', 'Kia', 'Seltos', 2022, 'Black', 34.99, FALSE, 1.3717794, 103.8539173),
('CAR005', 'Mazda', 'Mazda3', 2022, 'White', 39.99, TRUE, 1.3717794, 103.8539173),
('CAR006', 'Nissan', 'Altima', 2022, 'Yellow', 41.99, FALSE, 1.37146415, 103.8458867),
('CAR007', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.3718687, 103.8534834),
('CAR008', 'Chevrolet', 'Malibu', 2023, 'Pink', 43.99, TRUE, 1.3734289, 103.8511427),
('CAR009', 'BMW', '3 Series', 2022, 'Purple', 49.99, TRUE, 1.3690344, 103.8525089),
('CAR010', 'Volkswagen', 'Golf', 2022, 'Orange', 44.99, TRUE, 1.3666671, 103.8477911),
('CAR011', 'Toyota', 'Corolla', 2023, 'Blue', 35.99, TRUE, 1.3248322, 103.9335597),
('CAR012', 'Honda', 'Civic', 2022, 'Red', 32.99, TRUE, 1.3334902, 103.9428345),
('CAR013', 'Hyundai', 'Elantra', 2023, 'Black', 29.99, TRUE, 1.33198835, 103.9050014),
('CAR014', 'Kia', 'Seltos', 2022, 'Green', 34.99, FALSE, 1.325539600, 103.9344948),
('CAR015', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.31921635, 103.9451273),
('CAR016', 'Nissan', 'Altima', 2022, 'Yellow', 41.99, TRUE, 1.33198835, 103.9050014),
('CAR017', 'Ford', 'Focus', 2022, 'White', 37.99, TRUE, 1.3366844, 103.9283519),
('CAR018', 'Chevrolet', 'Malibu', 2023, 'Pink', 43.99, TRUE, 1.336865, 103.9293143),
('CAR019', 'BMW', '3 Series', 2022, 'Purple', 49.99, FALSE, 1.32412675, 103.9112575),
('CAR020', 'Volkswagen', 'Golf', 2022, 'Orange', 44.99, FALSE, 1.33615585, 103.934964),
('CAR021', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.3455006, 103.8521437),
('CAR022', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.35731545, 103.8458132),
('CAR023', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, TRUE, 1.3567242, 103.843465),
('CAR024', 'Kia', 'Seltos', 2022, 'Silver', 34.99, FALSE, 1.3567242, 103.843465),
('CAR025', 'Mazda', 'Mazda3', 2022, 'Black', 39.99, TRUE, 1.3497445, 103.8386818),
('CAR026', 'Nissan', 'Altima', 2022, 'Silver', 41.99, TRUE, 1.34609555, 103.8504653),
('CAR027', 'Ford', 'Focus', 2022, 'Navy', 37.99, TRUE, 1.3627589, 103.8327623),
('CAR028', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.3601274, 103.8326107),
('CAR029', 'BMW', '3 Series', 2022, 'Black', 49.99, FALSE, 1.35003245, 103.8531737),
('CAR030', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, TRUE, 1.3573729, 103.848478),
('CAR031', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.34460189, 103.7606773),
('CAR032', 'Honda', 'Civic', 2022, 'Black', 32.99, TRUE, 1.3510103, 103.7475202),
('CAR033', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, TRUE, 1.35037275, 103.7433906),
('CAR034', 'Kia', 'Seltos', 2022, 'Red', 34.99, FALSE, 1.35133210, 103.7495554),
('CAR035', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.3431934, 103.7565501),
('CAR036', 'Nissan', 'Altima', 2022, 'Silver', 41.99, TRUE, 1.3460204, 103.7444773),
('CAR037', 'Ford', 'Focus', 2022, 'Red', 37.99, FALSE, 1.3471008, 103.7499088),
('CAR038', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.3657232, 103.752372),
('CAR039', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.34619805, 103.7506954),
('CAR040', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, TRUE, 1.34665765, 103.7494082),
('CAR041', 'Toyota', 'Corolla', 2023, 'Red', 35.99, TRUE, 1.2736569, 103.806568),
('CAR042', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.29204669, 103.8269271),
('CAR043', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, TRUE, 1.2901627, 103.828593),
('CAR044', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.2822262, 103.8247),
('CAR045', 'Mazda', 'Mazda3', 2022, 'Red', 39.99, TRUE, 1.29065219, 103.8326076),
('CAR046', 'Nissan', 'Altima', 2022, 'Silver', 41.99, TRUE, 1.2822262, 103.8247),
('CAR047', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.27466215, 103.8097514),
('CAR048', 'Chevrolet', 'Malibu', 2023, 'Black', 43.99, TRUE, 1.28841695, 103.8173674),
('CAR049', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.2880798, 103.8153238),
('CAR050', 'Volkswagen', 'Golf', 2022, 'Black', 44.99, TRUE, 1.2822262, 103.8247),
('CAR051', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.38134825, 103.7617509),
('CAR052', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.3772955, 103.766173),
('CAR053', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, TRUE, 1.37999935, 103.7651484),
('CAR054', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.375492, 103.7710543),
('CAR055', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.3802487, 103.7662681),
('CAR056', 'Nissan', 'Altima', 2022, 'Silver', 41.99, TRUE, 1.37484145, 103.7651575),
('CAR057', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.37484145, 103.7651575),
('CAR058', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.37484145, 103.7651575),
('CAR059', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.38427035, 103.7636754),
('CAR060', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, TRUE, 1.3866348, 103.7630602),
('CAR061', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.3165728, 103.8073135),
('CAR062', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.33557825, 103.7710242),
('CAR063', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, TRUE, 1.33853615, 103.7744043),
('CAR064', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.33739869, 103.7747703),
('CAR065', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.33940739, 103.7718666),
('CAR066', 'Nissan', 'Altima', 2022, 'Silver', 41.99, TRUE, 1.33940739, 103.7718666),
('CAR067', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.3396678, 103.772688),
('CAR068', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.3191522, 103.8083721),
('CAR069', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.3396678, 103.772688),
('CAR070', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, TRUE, 1.3376138000, 103.7727287),
('CAR071', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.27779165, 103.8414036),
('CAR072', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.2759757, 103.8412094),
('CAR073', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, TRUE, 1.2759757, 103.8412094),
('CAR074', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.27743925, 103.8416672),
('CAR075', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.2976486, 103.8532702),
('CAR076', 'Nissan', 'Altima', 2022, 'Silver', 41.99, TRUE, 1.30093775, 103.8539812),
('CAR077', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.30093775, 103.8539812),
('CAR078', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.2762681, 103.8430291),
('CAR079', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.2850983, 103.8425388),
('CAR080', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, TRUE, 1.2990189, 103.8522801),
('CAR081', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.37783155, 103.7541469),
('CAR082', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.4019868999999998, 103.7508255),
('CAR083', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, TRUE, 1.39749555, 103.7451751),
('CAR084', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.3956971000000002, 103.7489617),
('CAR085', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.3768888, 103.7414365),
('CAR086', 'Nissan', 'Altima', 2022, 'Silver', 41.99, TRUE, 1.4025596000000002, 103.7479453),
('CAR087', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.3983155, 103.7459326),
('CAR088', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.38214855, 103.7437955),
('CAR089', 'BMW', '3 Series', 2022, 'Black', 49.99, FALSE, 1.3791581, 103.746254),
('CAR090', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, TRUE, 1.37865295, 103.7379709),
('CAR091', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.31116555, 103.7665386),
('CAR092', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.30359005, 103.763395),
('CAR093', 'Hyundai', 'Elantra', 2023, 'Black', 29.99, FALSE, 1.32141665, 103.7671519),
('CAR094', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.3030668, 103.7634541),
('CAR095', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, False, 1.3161184, 103.7702322),
('CAR096', 'Nissan', 'Altima', 2022, 'Silver', 41.99, TRUE, 1.31088855, 103.7696621),
('CAR097', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.31015975, 103.7701753),
('CAR098', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.3167528999999998, 103.7709037),
('CAR099', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.3021419, 103.763484),
('CAR100', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, FALSE, 1.3039684, 103.7691706),
('CAR101', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.3198016, 103.9028891),
('CAR102', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.31869815, 103.8995074),
('CAR103', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, TRUE, 1.3159569, 103.8858366),
('CAR104', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.3126055, 103.8965667),
('CAR105', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.3182037, 103.884774),
('CAR106', 'Nissan', 'Altima', 2022, 'Silver', 41.99, TRUE, 1.32702425, 103.8864787),
('CAR107', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.3169784, 103.876106),
('CAR108', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.32035965, 103.900866),
('CAR109', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.3240944, 103.8872736),
('CAR110', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, FALSE, 1.3174123, 103.8761805),
('CAR111', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, FALSE, 1.3657668, 103.8880873),
('CAR112', 'Honda', 'Civic', 2022, 'Silver', 32.99, FALSE, 1.3727613, 103.894626),
('CAR113', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, TRUE, 1.37316025, 103.8959609),
('CAR114', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.3628511, 103.8894678),
('CAR115', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.3694714, 103.8807576),
('CAR116', 'Nissan', 'Altima', 2022, 'Silver', 41.99, TRUE, 1.3776897, 103.8906057),
('CAR117', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.3728851, 103.8970035),
('CAR118', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.3497951, 103.8868098),
('CAR119', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.37345415, 103.879805),
('CAR120', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, TRUE, 1.3510918, 103.8892966),
('CAR121', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.3418045, 103.7361102),
('CAR122', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.34681155, 103.7330409),
('CAR123', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, TRUE, 1.33877265, 103.7356474),
('CAR124', 'Kia', 'Seltos', 2022, 'Silver', 34.99, FALSE, 1.34024175, 103.7439173),
('CAR125', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.3192073999999998, 103.7496705),
('CAR126', 'Nissan', 'Altima', 2022, 'Silver', 41.99, FALSE, 1.34196755, 103.7452451),
('CAR127', 'Ford', 'Focus', 2022, 'Silver', 37.99, FALSE, 1.3200627, 103.7410902),
('CAR128', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, FALSE, 1.34211815, 103.7456453),
('CAR129', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.3227813, 103.7398265),
('CAR130', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, TRUE, 1.3406979, 103.744576),
('CAR131', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.3396925, 103.7020233),
('CAR132', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.3396925, 103.7020233),
('CAR133', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, TRUE, 1.3426255, 103.7054145),
('CAR134', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.3396925, 103.7020233),
('CAR135', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, false, 1.34495245, 103.7200352),
('CAR136', 'Nissan', 'Altima', 2022, 'Silver', 41.99, TRUE, 1.3380286, 103.7005154),
('CAR137', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.34217355, 103.6994527),
('CAR138', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.34324575, 103.7041028),
('CAR139', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.35409055, 103.717264),
('CAR140', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, TRUE, 1.34391495, 103.701591),
('CAR141', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.31677585, 103.8618992),
('CAR142', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.31605155, 103.8613309),
('CAR143', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, TRUE, 1.328227, 103.8538411),
('CAR144', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.3200708, 103.8591472),
('CAR145', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.3200708, 103.8591472),
('CAR146', 'Nissan', 'Altima', 2022, 'Silver', 41.99, false, 1.3217621000000002, 103.866818),
('CAR147', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.3221921, 103.8680951),
('CAR148', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.3138205, 103.8730604),
('CAR149', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.31448915, 103.8510771),
('CAR150', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, false, 1.32409045, 103.8685965),
('CAR151', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.3026743, 103.9090363),
('CAR152', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.3054388, 103.91398),
('CAR153', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, false, 1.3062644, 103.8860968),
('CAR154', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.3038846000000002, 103.9097355),
('CAR155', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.3042909, 103.9083636),
('CAR156', 'Nissan', 'Altima', 2022, 'Silver', 41.99, TRUE, 1.30155905, 103.9084061),
('CAR157', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.30445565, 103.9181687),
('CAR158', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.30309225, 103.9087472),
('CAR159', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.30339185, 103.9085175),
('CAR160', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, TRUE, 1.3045562, 103.9124678),
('CAR161', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.371347, 103.9504027),
('CAR162', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.36750085, 103.9570595),
('CAR163', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, TRUE, 1.37414705, 103.9629831),
('CAR164', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.3684312, 103.9544746),
('CAR165', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.3733178999999998, 103.963512),
('CAR166', 'Nissan', 'Altima', 2022, 'Silver', 41.99, TRUE, 1.3716363, 103.9547637),
('CAR167', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.3745473, 103.9431372),
('CAR168', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.368142, 103.9525895),
('CAR169', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.3671693, 103.9595411),
('CAR170', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, TRUE, 1.37807085, 103.9406754),
('CAR171', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.4042572, 103.8987751),
('CAR172', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.4045546999999998, 103.89799),
('CAR173', 'Hyundai', 'Elantra', 2023, 'Black', 29.99, FALSE, 1.4041532, 103.89739190000002),
('CAR174', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.4022354, 103.9012737),
('CAR175', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.4041611, 103.8993277),
('CAR176', 'Nissan', 'Altima', 2022, 'Black', 41.99, false, 1.40192215, 103.9125165),
('CAR177', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.4045187, 103.9045428),
('CAR178', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.4034122, 103.8986832),
('CAR179', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.4033597, 103.9020688),
('CAR180', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, TRUE, 1.4026665, 103.89863309999998),
('CAR181', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.2933132, 103.8082566),
('CAR182', 'Honda', 'Civic', 2022, 'Black', 32.99, false, 1.3080632, 103.7831132),
('CAR183', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, false, 1.3109624, 103.7923652),
('CAR184', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.2927896, 103.8149021),
('CAR185', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.31110965, 103.7875704),
('CAR186', 'Nissan', 'Altima', 2022, 'Silver', 41.99, false, 1.3087603, 103.7860889),
('CAR187', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.2933132, 103.8082566),
('CAR188', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.3069607, 103.7937656),
('CAR189', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.3088902, 103.7938393),
('CAR190', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, TRUE, 1.2925466, 103.8119265),
('CAR191', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.44638775, 103.81546),
('CAR192', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.44682305, 103.8162704),
('CAR193', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, TRUE, 1.4503961, 103.8251679),
('CAR194', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.4513086000000002, 103.8197207),
('CAR195', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.4447108999999998, 103.8221941),
('CAR196', 'Nissan', 'Altima', 2022, 'Silver', 41.99, TRUE, 1.4498144, 103.8259267),
('CAR197', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.45089135, 103.81998670000002),
('CAR198', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.4466345, 103.8226039),
('CAR199', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.4502006, 103.8193297),
('CAR200', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, TRUE, 1.4500486, 103.8169968),
('CAR201', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.3952679, 103.8955298),
('CAR202', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.3842101, 103.903447),
('CAR203', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, TRUE, 1.3922557, 103.8998095),
('CAR204', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.3970617, 103.9012533),
('CAR205', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.38411315, 103.8944165),
('CAR206', 'Nissan', 'Altima', 2022, 'Silver', 41.99, TRUE, 1.3851877, 103.9039184),
('CAR207', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.3833418, 103.8945506),
('CAR208', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.3873064, 103.8955138),
('CAR209', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.3933702, 103.8765406),
('CAR210', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, TRUE, 1.3922622, 103.8925986),
('CAR211', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.3720696, 103.8725895),
('CAR212', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.3740375, 103.8733301),
('CAR213', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, TRUE, 1.3740979, 103.8718334),
('CAR214', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.37313275, 103.8756511),
('CAR215', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.34709245, 103.8731647),
('CAR216', 'Nissan', 'Altima', 2022, 'Silver', 41.99, TRUE, 1.34930175, 103.874858),
('CAR217', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.34709245, 103.8731647),
('CAR218', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.34628285, 103.8733039),
('CAR219', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.3545611000000002, 103.866869),
('CAR220', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, TRUE, 1.3586475, 103.8714748),
('CAR221', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.3530789, 103.9377775),
('CAR222', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.35635915, 103.9386619),
('CAR223', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, TRUE, 1.3563691, 103.9383839),
('CAR224', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.35544555, 103.9386597),
('CAR225', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.3526286, 103.9582156),
('CAR226', 'Nissan', 'Altima', 2022, 'Silver', 41.99, TRUE, 1.35219665, 103.9567494),
('CAR227', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.3588586, 103.9591596),
('CAR228', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.34567115, 103.9549067),
('CAR229', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.3588586, 103.9591596),
('CAR230', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, TRUE, 1.34764665, 103.9324642),
('CAR231', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.33472135, 103.8655948),
('CAR232', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.3357907, 103.8493367),
('CAR233', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, TRUE, 1.3352649, 103.8456343),
('CAR234', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.33461305, 103.8485762),
('CAR235', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.33466455, 103.8497284),
('CAR236', 'Nissan', 'Altima', 2022, 'Silver', 41.99, TRUE, 1.3351807, 103.8461957),
('CAR237', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.33252575, 103.8473865),
('CAR238', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.33911, 103.8465316),
('CAR239', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.3356469, 103.8500729),
('CAR240', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, TRUE, 1.3412581, 103.8555807),
('CAR241', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.4341774, 103.7907854),
('CAR242', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.4368561000000002, 103.7905396),
('CAR243', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, TRUE, 1.4363801, 103.789898),
('CAR244', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.4363801, 103.789898),
('CAR245', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.4410788, 103.7926743),
('CAR246', 'Nissan', 'Altima', 2022, 'Silver', 41.99, TRUE, 1.43829685, 103.8006662),
('CAR247', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.43943975, 103.7891633),
('CAR248', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.4342096000000002, 103.7901225),
('CAR249', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.44378285, 103.7999592),
('CAR250', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, TRUE, 1.4412271, 103.8033284),
('CAR251', 'Toyota', 'Corolla', 2023, 'Silver', 35.99, TRUE, 1.42859275, 103.8277737),
('CAR252', 'Honda', 'Civic', 2022, 'Silver', 32.99, TRUE, 1.4191253, 103.8397946),
('CAR253', 'Hyundai', 'Elantra', 2023, 'Silver', 29.99, TRUE, 1.4154972, 103.8330397),
('CAR254', 'Kia', 'Seltos', 2022, 'Silver', 34.99, TRUE, 1.4139485, 103.8352886),
('CAR255', 'Mazda', 'Mazda3', 2022, 'Silver', 39.99, TRUE, 1.429503, 103.847169),
('CAR256', 'Nissan', 'Altima', 2022, 'Silver', 41.99, TRUE, 1.4296809, 103.8430728),
('CAR257', 'Ford', 'Focus', 2022, 'Silver', 37.99, TRUE, 1.417086, 103.8321348),
('CAR258', 'Chevrolet', 'Malibu', 2023, 'Silver', 43.99, TRUE, 1.420915, 103.8352584),
('CAR259', 'BMW', '3 Series', 2022, 'Silver', 49.99, TRUE, 1.42874645, 103.8408678),
('CAR260', 'Volkswagen', 'Golf', 2022, 'Silver', 44.99, TRUE, 1.4180636, 103.8362361);

select * from car_available;
