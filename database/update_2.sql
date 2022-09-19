ALTER TABLE `imstats`.`course` 
ADD COLUMN `location` VARCHAR(100) NOT NULL AFTER `name`,
ADD COLUMN `url` VARCHAR(150) NOT NULL AFTER `location`;
