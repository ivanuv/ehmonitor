-- MySQL Script generated by MySQL Workbench
-- Wed Nov 25 18:07:43 2020
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema ehmonitor
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `ehmonitor` ;

-- -----------------------------------------------------
-- Schema ehmonitor
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `ehmonitor` DEFAULT CHARACTER SET utf8 ;
USE `ehmonitor` ;

-- -----------------------------------------------------
-- Table `ehmonitor`.`monitores`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ehmonitor`.`monitores` ;

CREATE TABLE IF NOT EXISTS `ehmonitor`.`monitores` (
  `idMonitor` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(45) NOT NULL,
  `usuario` VARCHAR(45) NOT NULL,
  `contrasena` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`idMonitor`))
ENGINE = InnoDB;

CREATE UNIQUE INDEX `usuario_UNIQUE` ON `ehmonitor`.`monitores` (`usuario` ASC);


-- -----------------------------------------------------
-- Table `ehmonitor`.`pacientes`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ehmonitor`.`pacientes` ;

CREATE TABLE IF NOT EXISTS `ehmonitor`.`pacientes` (
  `idPaciente` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(45) NOT NULL,
  `rut` INT(9) NOT NULL,
  `mapa_hogar` VARCHAR(255) NULL,
  `id_monitor` INT NOT NULL,
  PRIMARY KEY (`idPaciente`),
  CONSTRAINT `fk_Pacientes_Monitor1`
    FOREIGN KEY (`id_monitor`)
    REFERENCES `ehmonitor`.`monitores` (`idMonitor`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

CREATE INDEX `fk_Pacientes_Monitor1_idx` ON `ehmonitor`.`pacientes` (`id_monitor` ASC);

CREATE UNIQUE INDEX `rut_UNIQUE` ON `ehmonitor`.`pacientes` (`rut` ASC);

CREATE UNIQUE INDEX `mapa_hogar_UNIQUE` ON `ehmonitor`.`pacientes` (`mapa_hogar` ASC);


-- -----------------------------------------------------
-- Table `ehmonitor`.`sensores`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ehmonitor`.`sensores` ;

CREATE TABLE IF NOT EXISTS `ehmonitor`.`sensores` (
  `idSensor` INT NOT NULL AUTO_INCREMENT,
  `ubicacion` INT NOT NULL,
  `apodo_ubicacion` VARCHAR(45) NOT NULL,
  `estado` ENUM('activo', 'desactivado') NOT NULL,
  `tipo_sensor` ENUM('trisensor', 'caidasensor') NOT NULL,
  `disponible` TINYINT NOT NULL DEFAULT 1,
  `id_paciente` INT NOT NULL,
  PRIMARY KEY (`idSensor`),
  CONSTRAINT `fk_Sensores_trisensor_Pacientes1`
    FOREIGN KEY (`id_paciente`)
    REFERENCES `ehmonitor`.`pacientes` (`idPaciente`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

CREATE INDEX `fk_Sensores_trisensor_Pacientes1_idx` ON `ehmonitor`.`sensores` (`id_paciente` ASC);


-- -----------------------------------------------------
-- Table `ehmonitor`.`datos_sensor`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ehmonitor`.`datos_sensor` ;

CREATE TABLE IF NOT EXISTS `ehmonitor`.`datos_sensor` (
  `idDato` INT NOT NULL AUTO_INCREMENT,
  `fecha` DATETIME NOT NULL,
  `presencia` TINYINT NOT NULL,
  `id_sensor` INT NOT NULL,
  PRIMARY KEY (`idDato`),
  CONSTRAINT `fk_Datos_trisensor_Sensores_trisensor1`
    FOREIGN KEY (`id_sensor`)
    REFERENCES `ehmonitor`.`sensores` (`idSensor`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

CREATE INDEX `fk_Datos_trisensor_Sensores_trisensor1_idx` ON `ehmonitor`.`datos_sensor` (`id_sensor` ASC);

CREATE UNIQUE INDEX `index3` ON `ehmonitor`.`datos_sensor` (`fecha` ASC, `id_sensor` ASC);


-- -----------------------------------------------------
-- Table `ehmonitor`.`admin`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ehmonitor`.`admin` ;

CREATE TABLE IF NOT EXISTS `ehmonitor`.`admin` (
  `idAdmin` INT NOT NULL AUTO_INCREMENT,
  `usuario` VARCHAR(45) NULL,
  `contrasena` VARCHAR(255) NULL,
  PRIMARY KEY (`idAdmin`))
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- -----------------------------------------------------
-- Data for table `ehmonitor`.`admin`
-- -----------------------------------------------------
START TRANSACTION;
USE `ehmonitor`;
INSERT INTO `ehmonitor`.`admin` (`idAdmin`, `usuario`, `contrasena`) VALUES (1, 'monitorAdmin', '$2y$12$aqtjpzuwxr19552TKEunL.Y7blMu/HZAXvBxQoxBz7gxk/oW9Y/NC');

COMMIT;

