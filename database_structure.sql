/*
 Navicat Premium Data Transfer

 Source Server         : mysql
 Source Server Type    : MySQL
 Source Server Version : 80032 (8.0.32)
 Source Host           : localhost:3306
 Source Schema         : dataset12306_test

 Target Server Type    : MySQL
 Target Server Version : 80032 (8.0.32)
 File Encoding         : 65001

 Date: 28/08/2023 13:57:32
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for pii
-- ----------------------------
DROP TABLE IF EXISTS `pii`;
CREATE TABLE `pii`  (
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `account` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `idCard` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `phoneNum` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `fullName` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `name_index`(`name` ASC) USING BTREE,
  INDEX `fullname_index`(`fullName` ASC) USING BTREE,
  INDEX `account_index`(`account` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 418907 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for pwrepresentation_frequency_general
-- ----------------------------
DROP TABLE IF EXISTS `pwrepresentation_frequency_general`;
CREATE TABLE `pwrepresentation_frequency_general`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `pwStr` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `representationStructure` varchar(5000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'representation without vector.str',
  `representationStructureHash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'hash of representationStructure',
  `frequency` bigint NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `pwStr_index`(`pwStr` ASC) USING BTREE,
  INDEX `repStruct_hash_index`(`representationStructureHash` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1640622 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for pwrepresentation_general
-- ----------------------------
DROP TABLE IF EXISTS `pwrepresentation_general`;
CREATE TABLE `pwrepresentation_general`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `pwStr` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `representation` varchar(5000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'representation with vector.str',
  `representationHash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'hash of representation',
  `hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'hash of pwStr+representation',
  `representationStructure` varchar(5000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'representation without vector.str',
  `representationStructureHash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'hash of representationStructure',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `hash_unique`(`hash` ASC) USING BTREE,
  INDEX `pwStr_index`(`pwStr` ASC) USING BTREE,
  INDEX `rep_hash_index`(`representationHash` ASC) USING BTREE,
  INDEX `hash_index`(`hash` ASC) USING BTREE,
  INDEX `rep_struct_hash_index`(`representationStructureHash` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1640622 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for pwrepresentation_unique_general
-- ----------------------------
DROP TABLE IF EXISTS `pwrepresentation_unique_general`;
CREATE TABLE `pwrepresentation_unique_general`  (
  `pwStr` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `representationStructure` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `representationStructureHash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `representation` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `representationHash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `pwStr_unique`(`pwStr` ASC) USING BTREE,
  INDEX `pwStr_index`(`pwStr` ASC) USING BTREE,
  INDEX `rep_hash_index`(`representationHash` ASC) USING BTREE,
  INDEX `repStruct_hash_index`(`representationStructureHash` ASC) USING BTREE,
  INDEX `hash_index`(`hash` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 803541 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = 'The unique representation and structure of every password' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for representation_frequency_base_general
-- ----------------------------
DROP TABLE IF EXISTS `representation_frequency_base_general`;
CREATE TABLE `representation_frequency_base_general`  (
  `frequency` bigint NOT NULL DEFAULT 0,
  `representationStructureHash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'hash of representationStructure',
  INDEX `repStruct_hash_index`(`representationStructureHash` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for representation_frequency_general
-- ----------------------------
DROP TABLE IF EXISTS `representation_frequency_general`;
CREATE TABLE `representation_frequency_general`  (
  `frequency` bigint NOT NULL DEFAULT 0,
  `representationStructureHash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'hash of representationStructure',
  `representationStructure` varchar(5000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'representation without vector.str',
  INDEX `repStruct_hash_index`(`representationStructureHash` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
