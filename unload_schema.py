"""
Выгрузка схемы базы PostgresSQL
При вызове необходимо указать в параметрах:
- имя каталога для выгрузки файлов со схемой объектов. Если каталог отсутствует, он будет создан. 
  При создании файлов в каталоге старые файлы с совпадающими именами будут затёрты.
- Имя файла с дампом схемы, результата команды "pg_dump -h <host> -U <user> -d <bd> -s

Дамп схемы разрезается на отдельные файлы по объектам БД:
o	*.tab – таблицы
o	*.vw – представления
o	*.acl – гранты на таблицы
o	*.facl – гранты на функции
o	*.idx – индексы
o	*.seq – сиквенсы
o	*.fnc – функции
o	*.mvw – материализованные представления
o	*.ext – расширения (extension)
Схемы индексов сохраняются в отдельных файлах для каждого индекса.
Правила (rule) и триггеры (trigger) сохраняются в файле для соответствующей таблицы.

Проверялось на дампе от pg_dump 9.6.1.
Дампы схемы от pg_dump версий 9.4 и 9.5 не будут корректно разобраны данным модулем.
"""
import re
import os
import sys

# Начало любого блока со схемой объекта БД
###############################################################################################
#--
#-- TOC entry 4444 (class 0 OID 0)
mstart_block1 = re.compile('--')
mstart_block2 = re.compile('-- TOC entry (\d+) \(class \d+ OID \d+\)')

# Завершение дампа
###############################################################################################
#-- Completed on 2017-01-30 11:50:38
#
#--
#-- PostgreSQL database dump complete
#--
mend_dump1 = re.compile('-- Completed on .*')
mend_dump2 = re.compile('')
mend_dump3 = re.compile('--')
mend_dump4 = re.compile('-- PostgreSQL database dump complete')
mend_dump5 = re.compile('--')


# Далее набиты регэкспы для парсинга начала и конца блоков в дампе, относящихся к отдельным объектам.

# extension
###############################################################################################
#--
#-- TOC entry 1 (class 3079 OID 13223)
#-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner:
#--
mext1 = re.compile('--')
mext2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mext3 = re.compile('-- Name: ([\w-]+); Type: EXTENSION; Schema: ([\w-]+); Owner: (.*)')
mext4 = re.compile('--')

# Комменртарий к extension
###############################################################################################
#--
#-- TOC entry 5621 (class 0 OID 0)
#-- Dependencies: 1
#-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner:
#--
mext_comm1 = re.compile('--')
mext_comm2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mext_comm3 = re.compile('-- Dependencies: \d+')
mext_comm4 = re.compile('-- Name: EXTENSION ([\w-]+); Type: COMMENT; Schema: ([\w-]+); Owner: (.*)')
mext_comm5 = re.compile('--')

# Таблица
###############################################################################################
#--
#-- TOC entry 183 (class 1259 OID 45126)
#-- Dependencies: 1
#-- Name: abs_city; Type: TABLE; Schema: public; Owner: a.s.kulida
#--
mtable1 = re.compile('--')
mtable2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mtable3 = re.compile('-- Name: ([\"\w-]+); Type: TABLE; Schema: ([\w-]+); Owner: (.*)')
mtable4 = re.compile('--')

# Комментарий к таблице
###############################################################################################
#--
#-- TOC entry 4130 (class 0 OID 0)
#-- Dependencies: 185
#-- Name: TABLE abs_district; Type: COMMENT; Schema: public; Owner: a.s.kulida
#--
mtab_comment1 = re.compile('--')
mtab_comment2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mtab_comment3 = re.compile('-- Dependencies: \d+')
mtab_comment4 = re.compile('-- Name: TABLE (["\w-]+); Type: COMMENT; Schema: ([\w-]+); Owner: (.*)')
mtab_comment5 = re.compile('--')

# Права на таблицу
###############################################################################################
#--
#-- TOC entry 4133 (class 0 OID 0)
#-- Dependencies: 480
#-- Name: tei_roof; Type: ACL; Schema: public; Owner: a.s.kulida
#--
macl1 = re.compile('--')
macl2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
macl3 = re.compile('-- Dependencies: \d+')
macl4 = re.compile('-- Name: ([\w-]+); Type: ACL; Schema: ([\w-]+); Owner: (.*)')
macl5 = re.compile('--')

# Constraint
###############################################################################################
#--
#-- TOC entry 3979 (class 2606 OID 47521)
#-- Name: tei_roof tei_roof_pkey; Type: CONSTRAINT; Schema: public; Owner: a.s.kulida
#--
mtab_constr1 = re.compile('--')
mtab_constr2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mtab_constr3 = re.compile('-- Name: ([\w-]+) ([\w-]+); Type: CONSTRAINT; Schema: ([\w-]+); Owner: (.*)')
mtab_constr4 = re.compile('--')

# Foreign Key
###############################################################################################
#--
#-- TOC entry 3980 (class 2606 OID 48311)
#-- Name: tei_roof tei_roof_house_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: a.s.kulida
#--
mtab_fk_constr1 = re.compile('--')
mtab_fk_constr2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mtab_fk_constr3 = re.compile('-- Name: ([\w-]+) ([\w-]+); Type: FK CONSTRAINT; Schema: ([\w-]+); Owner: (.*)')
mtab_fk_constr4 = re.compile('--')

# Function
###############################################################################################
#--
#-- TOC entry 580 (class 1255 OID 45041)
#-- Name: billable_house(bigint, integer, integer); Type: FUNCTION; Schema: public; Owner: a.s.kulida
#--
mfunc1 = re.compile('--')
mfunc2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mfunc3 = re.compile('-- Name: ([\w-]+)\(.*\); Type: (FUNCTION|PROCEDURE); Schema: ([\w-]+); Owner: (.*)')
mfunc4 = re.compile('--')

# Function grants
###############################################################################################
#--
#-- TOC entry 4444 (class 0 OID 0)
#-- Dependencies: 566
#-- Name: update_bill_info(integer, integer); Type: ACL; Schema: public; Owner: a.s.kulida
#--
mfunc_acl1 = re.compile('--')
mfunc_acl2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mfunc_acl3 = re.compile('-- Dependencies: \d+')
mfunc_acl4 = re.compile('-- Name: ([\w-]+)\(.*\); Type: ACL; Schema: ([\w-]+); Owner: (.*)')
mfunc_acl5 = re.compile('--')

# Column comment
###############################################################################################
#--
#-- TOC entry 4129 (class 0 OID 0)
#-- Dependencies: 181
#-- Name: COLUMN audited_record.add_date; Type: COMMENT; Schema: public; Owner: a.s.kulida
#--
mcol_comment1 = re.compile('--')
mcol_comment2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mcol_comment3 = re.compile('-- Dependencies: \d+')
mcol_comment4 = re.compile('-- Name: COLUMN ([\"\w-]+).([\"\w-]+); Type: COMMENT; Schema: ([\w-]+); Owner: (.*)')
mcol_comment5 = re.compile('--')

# sequence
###############################################################################################
#--
#-- TOC entry 242 (class 1259 OID 45421)
#-- Name: ext_account_ext_account_id_seq; Type: SEQUENCE; Schema: public; Owner: a.s.kulida
#--
mseq1 = re.compile('--')
mseq2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mseq3 = re.compile('-- Name: ([\w-]+); Type: SEQUENCE; Schema: ([\w-]+); Owner: (.*)')
mseq4 = re.compile('--')

# sequence
###############################################################################################
#--
#-- TOC entry 5795 (class 0 OID 0)
#-- Dependencies: 242
#-- Name: ext_account_ext_account_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: a.s.kulida
#--
mseq_owned1 = re.compile('--')
mseq_owned2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mseq_owned3 = re.compile('-- Dependencies: \d+')
mseq_owned4 = re.compile('-- Name: ([\w-]+); Type: SEQUENCE OWNED BY; Schema: ([\w-]+); Owner: (.*)')
mseq_owned5 = re.compile('--')

# trigger
###############################################################################################
#--
#-- TOC entry 5312 (class 2620 OID 47910)
#-- Name: ext_flat-fias trigger_ext_record_after_delete; Type: TRIGGER; Schema: public; Owner: a.s.kulida
#--
mtrigger1 = re.compile('--')
mtrigger2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mtrigger3 = re.compile('-- Name: ([\w-]+) ([\w-]+); Type: TRIGGER; Schema: ([\w-]+); Owner: (.*)')
mtrigger4 = re.compile('--')

# view
###############################################################################################
#--
#-- TOC entry 202 (class 1259 OID 45212)
#-- Name: all_city; Type: VIEW; Schema: public; Owner: a.s.kulida
#--
mview1 = re.compile('--')
mview2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mview3 = re.compile('-- Name: ([\w-]+); Type: VIEW; Schema: ([\w-]+); Owner: (.*)')
mview4 = re.compile('--')

# index. К сожалению, в заголовке блока нет ссылки на таблицу.
###############################################################################################
#--
#-- TOC entry 5017 (class 1259 OID 47720)
#-- Name: repair_work_changelog_record_id_idx; Type: INDEX; Schema: public; Owner: a.s.kulida
#--
midx1 = re.compile('--')
midx2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
midx3 = re.compile('-- Name: ([\w-]+); Type: INDEX; Schema: ([\w-]+); Owner: (.*)')
midx4 = re.compile('--')

# constraint comment
###############################################################################################
#--
#-- TOC entry 5778 (class 0 OID 0)
#-- Dependencies: 232
#-- Name: CONSTRAINT account_num_length ON decision; Type: COMMENT; Schema: public; Owner: a.s.kulida
#--
mconstr_comment1 = re.compile('--')
mconstr_comment2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mconstr_comment3 = re.compile('-- Dependencies: \d+')
mconstr_comment4 = re.compile('-- Name: CONSTRAINT ([\w-]+) ON ([\w-]+); Type: COMMENT; Schema: ([\w-]+); Owner: (.*)')
mconstr_comment5 = re.compile('--')

# materialized view
###############################################################################################
#--
#-- TOC entry 300 (class 1259 OID 45856)
#-- Name: fee_totals; Type: MATERIALIZED VIEW; Schema: public; Owner: a.s.kulida
#--
mmat_view1 = re.compile('--')
mmat_view2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mmat_view3 = re.compile('-- Name: ([\w-]+); Type: MATERIALIZED VIEW; Schema: ([\w-]+); Owner: (.*)')
mmat_view4 = re.compile('--')

# default
###############################################################################################
#--
#-- TOC entry 4249 (class 2604 OID 46810)
#-- Name: benefits id; Type: DEFAULT; Schema: public; Owner: a.s.kulida
#--
mdefault1 = re.compile('--')
mdefault2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mdefault3 = re.compile('-- Name: ([\w-]+) ([\w-]+); Type: DEFAULT; Schema: ([\w-]+); Owner: (.*)')
mdefault4 = re.compile('--')

# rule
###############################################################################################
#--
#-- TOC entry 5613 (class 2618 OID 47755)
#-- Name: decision decision_delete_protect; Type: RULE; Schema: public; Owner: a.s.kulida
#--
mrule1 = re.compile('--')
mrule2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mrule3 = re.compile('-- Name: ([\w-]+) ([\w-]+); Type: RULE; Schema: ([\w-]+); Owner: (.*)')
mrule4 = re.compile('--')

# sequence comment
###############################################################################################
#--
#-- TOC entry 5957 (class 0 OID 0)
#-- Dependencies: 530
#-- Name: SEQUENCE trf_decision_number_seq; Type: COMMENT; Schema: public; Owner: lanit
#--
mseq_comment1 = re.compile('--')
mseq_comment2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mseq_comment3 = re.compile('-- Dependencies: \d+')
mseq_comment4 = re.compile('-- Name: SEQUENCE ([\w-]+); Type: COMMENT; Schema: ([\w-]+); Owner: (.*)')
mseq_comment5 = re.compile('--')

# Table partition
###############################################################################################
#--
#-- TOC entry 6431 (class 0 OID 0)
#-- Name: kpi_application_float_nsr_2021; Type: TABLE ATTACH; Schema: eff; Owner: -
#--
mtab_partition1 = re.compile('--')
mtab_partition2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mtab_partition3 = re.compile('-- Name: ([\w-]+); Type: TABLE ATTACH; Schema: ([\w-]+); Owner: (.*)')
mtab_partition4 = re.compile('--')

# View column comment
###############################################################################################
# --
# -- TOC entry 11339 (class 0 OID 0)
# -- Dependencies: 749
# -- Name: VIEW port_facility_vw; Type: COMMENT; Schema: infr; Owner: -
# --
mview_col_comment1 = re.compile('--')
mview_col_comment2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mview_col_comment3 = re.compile('-- Dependencies: \d+')
mview_col_comment4 = re.compile('-- Name: VIEW ([\w-]+); Type: COMMENT; Schema: ([\w-]+); Owner: (.*)')
mview_col_comment5 = re.compile('--')

# Index attach
###############################################################################################
# --
# -- TOC entry 9092 (class 0 OID 0)
# -- Name: kpi_disp_message_2019_ship_fk_doc_date_idx; Type: INDEX ATTACH; Schema: eff; Owner: -
# --
mind_partition1 = re.compile('--')
mind_partition2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mind_partition3 = re.compile('-- Name: ([\w-]+); Type: INDEX ATTACH; Schema: ([\w-]+); Owner: (.*)')
mind_partition4 = re.compile('--')

# Schema
###############################################################################################
# --
# -- TOC entry 13 (class 2615 OID 20683)
# -- Name: etp; Type: SCHEMA; Schema: -; Owner: -
# --
mschema1 = re.compile('--')
mschema2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mschema3 = re.compile('-- Name: ([\w-]+); Type: SCHEMA; Schema: ([\w-]+); Owner: (.*)')
mschema4 = re.compile('--')

# Procedure comment
###############################################################################################
# --
# -- TOC entry 10094 (class 0 OID 0)
# -- Dependencies: 1585
# -- Name: PROCEDURE refman_get_selection_sp(IN v_tab_code character varying, INOUT ref refcursor, IN v_uuid uuid); Type: COMMENT; Schema: rel; Owner: -
# --
mproc_comment1 = re.compile('--')
mproc_comment2 = re.compile('-- TOC entry \d+ \(class \d+ OID \d+\)')
mproc_comment3 = re.compile('-- Dependencies: \d+')
mproc_comment4 = re.compile('-- Name: (PROCEDURE|FUNCTION) ([\w-]+)\(.*\); Type: COMMENT; Schema: ([\w-]+); Owner: (.*)')
mproc_comment5 = re.compile('--')

def parse_dump_file(dump_file, debug):
	"""
	Парсинг дамп-файла
		dump_file - имя дамп-файла
	Возвращает список кортежей вида (имя_файла, стартовая_строка, конечная_строка)
	"""

	# Предыдущие прочитанные из дамп-файла строки
	s_p1 = ''
	s_p2 = ''
	s_p3 = ''
	s_p4 = ''
	s_p5 = ''

	# Номер текущей прочитанной строки
	line_no = 0

	# Текущий разбираемый блок с описанием объекта БД
	b_no = 0
	e_no = 0
	name = ""

	# Подготавливыаемый список кортежей вида (имя_файла, стартовая_строка, конечная_строка)
	L = []

	# Сюда заносим с нулём номера строк для начала блоков и помечаем единицей те, которые удалось распарсить
	SBL = {}

	for line in open(dump_file, mode="r", encoding="utf-8"):
		line_no += 1
		end_block = False
		#print(line, end='')

		#print("{0} {1}".format(line_no, line))

		mo1 = mstart_block1.match(s_p1)
		mo2 = mstart_block2.match(line)
		if mo1 and mo2:
			#print("Start block for entry =", mo2.group(1))
			#print("start block {0}".format(line_no-1))
			SBL[line_no-1] = 0
			if b_no != 0:
				e_no = line_no - 2
				end_block = True

		mo1 = mend_dump1.match(s_p4)
		mo2 = mend_dump2.match(s_p3)
		mo3 = mend_dump3.match(s_p2)
		mo4 = mend_dump4.match(s_p1)
		mo5 = mend_dump5.match(line)
		if mo1 and mo2 and mo3 and mo4 and mo5:
			#print("End dump")
			if b_no != 0:
				e_no = line_no - 5
				end_block = True

		if end_block:
			L.append((name, b_no, e_no))

		mo1 = mtable1.match(s_p3)
		mo2 = mtable2.match(s_p2)
		mo3 = mtable3.match(s_p1)
		mo4 = mtable4.match(line)
		if mo1 and mo2 and mo3 and mo4:
			#print(mo3.group(2), mo3.group(1), end=" Table\n")
			b_no = line_no + 1
			name = "{0}.{1}".format(mo3.group(2), mo3.group(1))
			SBL[line_no-3] = 1
			#print(name, end=" Table\n")

		mo1 = mtab_comment1.match(s_p4)
		mo2 = mtab_comment2.match(s_p3)
		mo3 = mtab_comment3.match(s_p2)
		mo4 = mtab_comment4.match(s_p1)
		mo5 = mtab_comment5.match(line)
		if mo1 and mo2 and mo3 and mo4 and mo5:
			#print(mo4.group(1), end=" Comment\n")
			b_no = line_no + 1
			name = "{0}.{1}".format(mo4.group(2), mo4.group(1))
			SBL[line_no-4] = 1
			#print(name, end=" Table comment\n")

		mo1 = macl1.match(s_p4)
		mo2 = macl2.match(s_p3)
		mo3 = macl3.match(s_p2)
		mo4 = macl4.match(s_p1)
		mo5 = macl5.match(line)
		if mo1 and mo2 and mo3 and mo4 and mo5:
			#print(mo4.group(1), end=" ACL\n")
			b_no = line_no + 1
			name = "{0}.{1}".format(mo4.group(2), mo4.group(1))
			SBL[line_no-4] = 1

		mo1 = mtab_constr1.match(s_p3)
		mo2 = mtab_constr2.match(s_p2)
		mo3 = mtab_constr3.match(s_p1)
		mo4 = mtab_constr4.match(line)
		if mo1 and mo2 and mo3 and mo4:
			#print(mo3.group(1), end=" Constraint\n")
			b_no = line_no + 1
			name = "{0}.{1}".format(mo3.group(3), mo3.group(1))
			SBL[line_no-3] = 1

		mo1 = mtab_fk_constr1.match(s_p3)
		mo2 = mtab_fk_constr2.match(s_p2)
		mo3 = mtab_fk_constr3.match(s_p1)
		mo4 = mtab_fk_constr4.match(line)
		if mo1 and mo2 and mo3 and mo4:
			#print(mo3.group(1), end=" FK constraint\n")
			b_no = line_no + 1
			name = "{0}.{1}".format(mo3.group(3), mo3.group(1))
			SBL[line_no-3] = 1

		mo1 = mfunc1.match(s_p3)
		mo2 = mfunc2.match(s_p2)
		mo3 = mfunc3.match(s_p1)
		mo4 = mfunc4.match(line)
		if mo1 and mo2 and mo3 and mo4:
			#print(mo3.group(1), end=" Function\n")
			b_no = line_no + 1
			name = "{0}.{1}".format(mo3.group(3), mo3.group(1))
			SBL[line_no-3] = 1

		mo1 = mfunc_acl1.match(s_p4)
		mo2 = mfunc_acl2.match(s_p3)
		mo3 = mfunc_acl3.match(s_p2)
		mo4 = mfunc_acl4.match(s_p1)
		mo5 = mfunc_acl5.match(line)
		if mo1 and mo2 and mo3 and mo4 and mo5:
			#print(mo4.group(1), end=" func ACL\n")
			b_no = line_no + 1
			name = "{0}.{1}".format(mo4.group(3), mo4.group(1))
			SBL[line_no-4] = 1

		mo1 = mcol_comment1.match(s_p4)
		mo2 = mcol_comment2.match(s_p3)
		mo3 = mcol_comment3.match(s_p2)
		mo4 = mcol_comment4.match(s_p1)
		mo5 = mcol_comment5.match(line)
		if mo1 and mo2 and mo3 and mo4 and mo5:
			#print(mo4.group(1), end=" func ACL\n")
			b_no = line_no + 1
			name = "{0}.{1}".format(mo4.group(3), mo4.group(1))
			SBL[line_no-4] = 1

		mo1 = mseq1.match(s_p3)
		mo2 = mseq2.match(s_p2)
		mo3 = mseq3.match(s_p1)
		mo4 = mseq4.match(line)
		if mo1 and mo2 and mo3 and mo4:
			#print(mo3.group(1), end=" Function\n")
			b_no = line_no + 1
			name = "{0}.{1}".format(mo3.group(2), mo3.group(1))
			SBL[line_no-3] = 1

		mo1 = mseq_owned1.match(s_p4)
		mo2 = mseq_owned2.match(s_p3)
		mo3 = mseq_owned3.match(s_p2)
		mo4 = mseq_owned4.match(s_p1)
		mo5 = mseq_owned5.match(line)
		if mo1 and mo2 and mo3 and mo4 and mo5:
			#print(mo4.group(1), end=" func ACL\n")
			b_no = line_no + 1
			name = "{0}.{1}".format(mo4.group(2), mo4.group(1))
			SBL[line_no-4] = 1

		mo1 = mtrigger1.match(s_p3)
		mo2 = mtrigger2.match(s_p2)
		mo3 = mtrigger3.match(s_p1)
		mo4 = mtrigger4.match(line)
		if mo1 and mo2 and mo3 and mo4:
			#print(mo3.group(1), end=" Function\n")
			b_no = line_no + 1
			name = "{0}.{1}".format(mo3.group(3), mo3.group(1))
			SBL[line_no-3] = 1

		mo1 = mview1.match(s_p3)
		mo2 = mview2.match(s_p2)
		mo3 = mview3.match(s_p1)
		mo4 = mview4.match(line)
		if mo1 and mo2 and mo3 and mo4:
			#print(mo3.group(1), end=" Function\n")
			b_no = line_no + 1
			name = "{0}.{1}".format(mo3.group(2), mo3.group(1))
			SBL[line_no-3] = 1

		mo1 = midx1.match(s_p3)
		mo2 = midx2.match(s_p2)
		mo3 = midx3.match(s_p1)
		mo4 = midx4.match(line)
		if mo1 and mo2 and mo3 and mo4:
			#print(mo3.group(1), end=" Function\n")
			b_no = line_no + 1
			name = "{0}.indexes".format(mo3.group(2))
			SBL[line_no-3] = 1

		mo1 = mconstr_comment1.match(s_p4)
		mo2 = mconstr_comment2.match(s_p3)
		mo3 = mconstr_comment3.match(s_p2)
		mo4 = mconstr_comment4.match(s_p1)
		mo5 = mconstr_comment5.match(line)
		if mo1 and mo2 and mo3 and mo4 and mo5:
			#print(mo4.group(1), end=" func ACL\n")
			b_no = line_no + 1
			name = "{0}.{1}".format(mo4.group(3), mo4.group(1))
			SBL[line_no-4] = 1

		mo1 = mmat_view1.match(s_p3)
		mo2 = mmat_view2.match(s_p2)
		mo3 = mmat_view3.match(s_p1)
		mo4 = mmat_view4.match(line)
		if mo1 and mo2 and mo3 and mo4:
			#print(mo3.group(1), end=" Function\n")
			b_no = line_no + 1
			name = "{0}.{1}".format(mo3.group(2), mo3.group(1))
			SBL[line_no-3] = 1

		mo1 = mdefault1.match(s_p3)
		mo2 = mdefault2.match(s_p2)
		mo3 = mdefault3.match(s_p1)
		mo4 = mdefault4.match(line)
		if mo1 and mo2 and mo3 and mo4:
			#print(mo3.group(1), end=" Function\n")
			b_no = line_no + 1
			name = "{0}.{1}".format(mo3.group(3), mo3.group(1))
			SBL[line_no-3] = 1

		mo1 = mrule1.match(s_p3)
		mo2 = mrule2.match(s_p2)
		mo3 = mrule3.match(s_p1)
		mo4 = mrule4.match(line)
		if mo1 and mo2 and mo3 and mo4:
			#print(mo3.group(1), end=" Function\n")
			b_no = line_no + 1
			name = "{0}.{1}".format(mo3.group(3), mo3.group(1))
			SBL[line_no-3] = 1

		mo1 = mext1.match(s_p3)
		mo2 = mext2.match(s_p2)
		mo3 = mext3.match(s_p1)
		mo4 = mext4.match(line)
		if mo1 and mo2 and mo3 and mo4:
			#print(mo3.group(1), end=" Function\n")
			b_no = line_no + 1
			name = "aaa_ext"
			SBL[line_no-3] = 1

		mo1 = mext_comm1.match(s_p4)
		mo2 = mext_comm2.match(s_p3)
		mo3 = mext_comm3.match(s_p2)
		mo4 = mext_comm4.match(s_p1)
		mo5 = mext_comm5.match(line)
		if mo1 and mo2 and mo3 and mo4 and mo5:
			#print(mo3.group(1), end=" Function\n")
			b_no = line_no + 1
			name = "aaa_ext"
			SBL[line_no-4] = 1

		mo1 = mseq_comment1.match(s_p4)
		mo2 = mseq_comment2.match(s_p3)
		mo3 = mseq_comment3.match(s_p2)
		mo4 = mseq_comment4.match(s_p1)
		mo5 = mseq_comment5.match(line)
		if mo1 and mo2 and mo3 and mo4 and mo5:
			#print(mo3.group(1), end=" Function\n")
			b_no = line_no + 1
			name = "{0}.{1}_seq".format(mo4.group(2), mo4.group(1))
			SBL[line_no-4] = 1

		mo1 = mtab_partition1.match(s_p3)
		mo2 = mtab_partition2.match(s_p2)
		mo3 = mtab_partition3.match(s_p1)
		mo4 = mtab_partition4.match(line)
		if mo1 and mo2 and mo3 and mo4:
			#print(mo3.group(1), end=" Function\n")
			b_no = line_no + 1
			name = "{0}.partitions".format(mo3.group(2))
			SBL[line_no-3] = 1

		mo1 = mind_partition1.match(s_p3)
		mo2 = mind_partition2.match(s_p2)
		mo3 = mind_partition3.match(s_p1)
		mo4 = mind_partition4.match(line)
		if mo1 and mo2 and mo3 and mo4:
			#print(mo3.group(1), end=" Function\n")
			b_no = line_no + 1
			name = "{0}.partitions".format(mo3.group(2))
			SBL[line_no-3] = 1

		mo1 = mview_col_comment1.match(s_p4)
		mo2 = mview_col_comment2.match(s_p3)
		mo3 = mview_col_comment3.match(s_p2)
		mo4 = mview_col_comment4.match(s_p1)
		mo5 = mview_col_comment5.match(line)
		if mo1 and mo2 and mo3 and mo4 and mo5:
			#print(mo3.group(1), end=" Function\n")
			b_no = line_no + 1
			name = "{0}.{1}".format(mo4.group(2), mo4.group(1))
			SBL[line_no-4] = 1

		mo1 = mschema1.match(s_p3)
		mo2 = mschema2.match(s_p2)
		mo3 = mschema3.match(s_p1)
		mo4 = mschema4.match(line)
		if mo1 and mo2 and mo3 and mo4:
			#print(mo3.group(1), end=" Function\n")
			b_no = line_no + 1
			name = "aaa_schemas"
			SBL[line_no-3] = 1

		mo1 = mproc_comment1.match(s_p4)
		mo2 = mproc_comment2.match(s_p3)
		mo3 = mproc_comment3.match(s_p2)
		mo4 = mproc_comment4.match(s_p1)
		mo5 = mproc_comment5.match(line)
		if mo1 and mo2 and mo3 and mo4 and mo5:
			#print(mo3.group(1), end=" Function\n")
			b_no = line_no + 1
			name = "{0}.{1}".format(mo4.group(3), mo4.group(2))
			SBL[line_no-4] = 1
			#rint(name, end=" Function\n")

		s_p5 = s_p4
		s_p4 = s_p3
		s_p3 = s_p2
		s_p2 = s_p1
		s_p1 = line
	for x in SBL:
		if SBL[x] == 0:
			print("{0} line - unknown block".format(x))
	return L
		
def create_descr(L, dir_name, dump_file, debug):
	"""
	Формирует файлы с описаниями объектов
	Входные параметры:
		L - список из кортежей (имя файла, стартовая_строка, конечная строка)
		dir_name - каталог для формирования файлов
		dump_file - имя дамп-файла, из которого формируются отдельные файлы с описаниями объектов
	"""
	s = ""
	D = {}
	dump_file_line_no = 0
	out_lines = []

	if not os.path.exists(dir_name):
		os.makedirs(dir_name)
	file = open(dump_file, mode="r", encoding="utf-8")

	for x in L:
		if debug: print("{0} {1} {2}".format(x[0], x[1], x[2]))
		while dump_file_line_no < x[1]:
			dump_file_line_no += 1
			s = file.readline()
		fname = os.path.join(dir_name, x[0].replace('"','') + ".sql")
		if not fname in D:
			fo = open(fname, mode="w", encoding="utf-8")
			D[fname] = 1
		else:
			fo = open(fname, mode="a", encoding="utf-8")
		out_lines = []			
		while dump_file_line_no <= x[2]:
			out_lines.append(s)
			dump_file_line_no += 1
			s = file.readline()
		
		# Удаляем пустые строки в начале и в конце блока
		while len(out_lines)>0 and out_lines[0] == '\n':
			out_lines.pop(0);
		while len(out_lines)>0 and out_lines[-1] == '\n':
			out_lines.pop();

		for s in out_lines:
			fo.write(s)

		fo.close()
	file.close()
	
def unload(dir_name, dump_file, debug = False):
	L = parse_dump_file(dump_file, debug)
	create_descr(L, dir_name, dump_file, debug)
	
if __name__ == "__main__":
	from optparse import OptionParser
	parser = OptionParser()
	parser.add_option("-i", "--in_file", dest="in_file", help="File as a result from pg_dump -s")
	parser.add_option("-o", "--out_dir", dest="out_dir", help="Unload directory")
	(options, args) = parser.parse_args()
	if not options.in_file:
		parser.error("option -i (--in_file) should be set")
	if not options.out_dir:
		parser.error("option -o (--out_dir) should be set")
	if not os.path.isfile(options.in_file):
		print("File {0} does not exist".format(options.in_file), file=sys.stderr)
		exit(1)
	unload(options.out_dir, options.in_file)
