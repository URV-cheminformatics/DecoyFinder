CREATE  TABLE IF NOT EXISTS Molecules (
  `inchikey` CHAR(25) NOT NULL ,
  `maccs` TEXT NOT NULL ,
  `rotatable_bonds` INT NOT NULL ,
  `weight` DECIMAL(9,4) NOT NULL ,
  `logp` DECIMAL(6,3) NOT NULL ,
  `hba` INT NOT NULL ,
  `hbd` INT NOT NULL ,
  `mol` TEXT NOT NULL ,
  `tpsa` DECIMAL(7,3) NOT NULL ,
  PRIMARY KEY (`inchikey`)
  )

