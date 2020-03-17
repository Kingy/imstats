CREATE TABLE `country` (
  `cty_code` varchar(3) NOT NULL,
  `cty_name` varchar(100) NOT NULL,
  `crt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cty_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `course` (
  `course_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `crt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`course_id`)
) ENGINE=InnoDB AUTO_INCREMENT=184 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `imstats_codes` (
  `code_scm_val` varchar(50) NOT NULL,
  `code_scm` varchar(50) NOT NULL,
  `code_val` varchar(3) NOT NULL,
  `code_desc` varchar(100) NOT NULL,
  `crt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`code_scm_val`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `race` (
  `race_id` int NOT NULL AUTO_INCREMENT,
  `course_id` int DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `race_date` date NOT NULL,
  `crt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`race_id`),
  KEY `FK_race_course` (`course_id`),
  CONSTRAINT `FK_race_course` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `race_results` (
  `result_id` int NOT NULL AUTO_INCREMENT,
  `race_id` int DEFAULT NULL,
  `part_name` varchar(150) NOT NULL,
  `cty_code` varchar(3) DEFAULT NULL,
  `part_div_tp` varchar(6) NOT NULL,
  `part_gen` varchar(1) NOT NULL,
  `part_div_rank` int NOT NULL,
  `part_gen_rank` int NOT NULL,
  `part_ovrl_rank` int NOT NULL,
  `part_tot_time` time NOT NULL,
  `crt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`result_id`),
  KEY `FK_result_race` (`race_id`),
  KEY `FK_result_cty` (`cty_code`),
  CONSTRAINT `FK_result_cty` FOREIGN KEY (`cty_code`) REFERENCES `country` (`cty_code`),
  CONSTRAINT `FK_result_race` FOREIGN KEY (`race_id`) REFERENCES `race` (`race_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `result_det` (
  `result_det_id` int NOT NULL AUTO_INCREMENT,
  `result_id` int DEFAULT NULL,
  `event_tp` varchar(6) NOT NULL,
  `div_rank` int NOT NULL,
  `gen_rank` int NOT NULL,
  `ovrl_rank` int NOT NULL,
  `tot_time` time NOT NULL,
  `t1_time` time NOT NULL,
  `t2_time` time NOT NULL,
  `crt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`result_det_id`),
  KEY `FK_result_det_result` (`result_id`),
  CONSTRAINT `FK_result_det_result` FOREIGN KEY (`result_id`) REFERENCES `race_results` (`result_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
