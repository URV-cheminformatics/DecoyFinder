CREATE  TABLE IF NOT EXISTS Molecules (
  `inchikey` CHAR(25) NOT NULL ,
  `smiles` TEXT NOT NULL ,
  `maccs` TEXT NOT NULL ,
  `rotatable_bonds` INT NOT NULL ,
  `weight` DECIMAL(9,4) NOT NULL ,
  `logp` DECIMAL(6,3) NOT NULL ,
  `hba` INT NOT NULL ,
  `hbd` INT NOT NULL ,
  `mol` BLOB NOT NULL ,
  `tpsa` DECIMAL(7,3) NOT NULL ,
  PRIMARY KEY (`inchikey`)
  );

CREATE UNIQUE INDEX IF NOT EXISTS maccs ON Molecules (`maccs`);
CREATE UNIQUE INDEX IF NOT EXISTS smiles ON Molecules (`smiles`);

CREATE INDEX IF NOT EXISTS rotatable_bonds ON Molecules (`rotatable_bonds`);
CREATE INDEX IF NOT EXISTS weight ON Molecules (`weight`);
CREATE INDEX IF NOT EXISTS logp ON Molecules (`logp`);
CREATE INDEX IF NOT EXISTS hba ON Molecules (`hba`);
CREATE INDEX IF NOT EXISTS hbd ON Molecules (`hbd`);
CREATE INDEX IF NOT EXISTS mol ON Molecules (`mol`);
CREATE INDEX IF NOT EXISTS tpsa ON Molecules (`tpsa`);
