SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

CREATE SCHEMA IF NOT EXISTS `decoyfinder` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci ;
USE `decoyfinder` ;

-- -----------------------------------------------------
-- Table `decoyfinder`.`Molecules`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `decoyfinder`.`Molecules` (
  `inchikey` CHAR(25) NOT NULL ,
  `maccs` TEXT NOT NULL ,
  `rotatable_bonds` INT NOT NULL ,
  `weight` DECIMAL(9,4) NOT NULL ,
  `logp` DECIMAL(6,3) NOT NULL ,
  `hba` INT NOT NULL ,
  `hbd` INT NOT NULL ,
  `mol` TEXT NOT NULL ,
  `tpsa` DECIMAL(7,3) NOT NULL ,
  PRIMARY KEY (`inchikey`) ,
  UNIQUE INDEX `inchikey_UNIQUE` (`inchikey` ASC) )
-- ENGINE = MyISAM;
ENGINE = InnoDB;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
