FUNCTION_BLOCK scale_to_real
  VAR_INPUT
    raw_input_value : UINT;
  END_VAR
  VAR_OUTPUT
    scaled_real : REAL;
  END_VAR
  VAR_INPUT
    real_max : REAL;
    real_min : REAL;
  END_VAR
  VAR
    raw_max : UINT := 65535;
    raw_min : UINT := 0;
    rate : REAL;
    offset : REAL;
  END_VAR

  rate := (real_max - real_min) / UINT_TO_REAL(raw_max - raw_min);
  offset := real_min - UINT_TO_REAL(raw_min)*rate;
  scaled_real := UINT_TO_REAL(raw_input_value)*rate + offset;
END_FUNCTION_BLOCK

FUNCTION_BLOCK scale_to_uint
  VAR_INPUT
    real_in : REAL;
  END_VAR
  VAR_OUTPUT
    uint_out : UINT;
  END_VAR
  VAR
    _TMP_DIV1_OUT : REAL;
    _TMP_MUL4_OUT : REAL;
    _TMP_REAL_TO_UINT6_OUT : UINT;
  END_VAR

  _TMP_DIV1_OUT := DIV(real_in, 100.0);
  _TMP_MUL4_OUT := MUL(_TMP_DIV1_OUT, 65535.0);
  _TMP_REAL_TO_UINT6_OUT := REAL_TO_UINT(_TMP_MUL4_OUT);
  uint_out := _TMP_REAL_TO_UINT6_OUT;
END_FUNCTION_BLOCK

FUNCTION_BLOCK flow_control
  VAR
    flow_k : REAL := 1.0;
    flow_ti : REAL := 999.0;
    flow_td : REAL := 0.0;
  END_VAR
  VAR_INPUT
    product_flow : UINT := 6554;
  END_VAR
  VAR
    product_flow_real : REAL := 100.0;
    cycle_time : TIME := T#50ms;
    pos_update_real : REAL := 0.0;
    curr_pos_real : REAL := 60.9;
  END_VAR
  VAR_OUTPUT
    new_pos : UINT := 35000;
  END_VAR
  VAR_INPUT
    curr_pos : UINT := 35000;
  END_VAR
  VAR
    flow_set_real : REAL := 100.0;
  END_VAR
  VAR_INPUT
    flow_set_in : UINT := 6554;
  END_VAR
  VAR
    scale_to_real0 : scale_to_real;
    scale_to_real1 : scale_to_real;
    flow_max : REAL := 500.0;
    flow_min : REAL := 0.0;
    pos_min : REAL := 0.0;
    pos_max : REAL := 100.0;
    scale_to_real2 : scale_to_real;
    scale_to_uint0 : scale_to_uint;
    _TMP_SUB59_OUT : REAL;
    _TMP_MUL60_OUT : REAL;
    _TMP_ADD58_OUT : REAL;
    _TMP_LIMIT40_OUT : REAL;
  END_VAR

  _TMP_SUB59_OUT := SUB(flow_set_real, product_flow_real);
  _TMP_MUL60_OUT := MUL(_TMP_SUB59_OUT, flow_k);
  pos_update_real := _TMP_MUL60_OUT;
  scale_to_real0(raw_input_value := product_flow, real_max := flow_max, real_min := flow_min);
  product_flow_real := scale_to_real0.scaled_real;
  scale_to_real1(raw_input_value := flow_set_in, real_max := flow_max, real_min := flow_min);
  flow_set_real := scale_to_real1.scaled_real;
  scale_to_real2(raw_input_value := curr_pos, real_max := pos_max, real_min := pos_min);
  curr_pos_real := scale_to_real2.scaled_real;
  _TMP_ADD58_OUT := ADD(curr_pos_real, pos_update_real);
  _TMP_LIMIT40_OUT := LIMIT(pos_min, _TMP_ADD58_OUT, pos_max);
  scale_to_uint0(real_in := _TMP_LIMIT40_OUT);
  new_pos := scale_to_uint0.uint_out;
END_FUNCTION_BLOCK

FUNCTION_BLOCK composition_control
  VAR
    a_in_purge_real : REAL := 47.00;
  END_VAR
  VAR_INPUT
    a_in_purge : UINT := 32000;
  END_VAR
  VAR
    a_setpoint_real : REAL := 47.00;
  END_VAR
  VAR_INPUT
    a_setpoint : UINT := 32000;
    curr_pos : UINT := 16000;
  END_VAR
  VAR
    valve_pos_real : REAL := 25.0;
    pos_update_real : REAL := 0.0;
    valve_pos_nominal : REAL := 25.0;
  END_VAR
  VAR_OUTPUT
    new_pos : UINT := 16000;
  END_VAR
  VAR
    composition_k : REAL := 1.0;
    composition_ti : REAL := 99.0;
    cycle_time : TIME := T#50ms;
    scale_to_real3 : scale_to_real;
    scale_to_real2 : scale_to_real;
    scale_to_uint0 : scale_to_uint;
    comp_max : REAL := 100.0;
    comp_min : REAL := 0.0;
    pos_max : REAL := 100.0;
    pos_min : REAL := 0.0;
    scale_to_real0 : scale_to_real;
    _TMP_SUB45_OUT : REAL;
    _TMP_MUL46_OUT : REAL;
    _TMP_ADD42_OUT : REAL;
    _TMP_LIMIT44_OUT : REAL;
  END_VAR

  _TMP_SUB45_OUT := SUB(a_setpoint_real, a_in_purge_real);
  _TMP_MUL46_OUT := MUL(_TMP_SUB45_OUT, composition_k);
  pos_update_real := _TMP_MUL46_OUT;
  scale_to_real3(raw_input_value := a_in_purge, real_max := comp_max, real_min := comp_min);
  a_in_purge_real := scale_to_real3.scaled_real;
  scale_to_real2(raw_input_value := a_setpoint, real_max := comp_max, real_min := comp_min);
  a_setpoint_real := scale_to_real2.scaled_real;
  _TMP_ADD42_OUT := ADD(valve_pos_real, pos_update_real);
  _TMP_LIMIT44_OUT := LIMIT(pos_min, _TMP_ADD42_OUT, pos_max);
  scale_to_uint0(real_in := _TMP_LIMIT44_OUT);
  new_pos := scale_to_uint0.uint_out;
  scale_to_real0(raw_input_value := curr_pos, real_max := pos_max, real_min := pos_min);
  valve_pos_real := scale_to_real0.scaled_real;
END_FUNCTION_BLOCK

FUNCTION_BLOCK scale_to_signed
  VAR_INPUT
    input_uint : UINT;
  END_VAR
  VAR_OUTPUT
    output_int : INT;
  END_VAR
  VAR
    _TMP_DIV3_OUT : UINT;
    _TMP_ABS8_OUT : UINT;
    _TMP_UINT_TO_INT9_OUT : INT;
  END_VAR

  _TMP_DIV3_OUT := DIV(input_uint, 2);
  _TMP_ABS8_OUT := ABS(_TMP_DIV3_OUT);
  _TMP_UINT_TO_INT9_OUT := UINT_TO_INT(_TMP_ABS8_OUT);
  output_int := _TMP_UINT_TO_INT9_OUT;
END_FUNCTION_BLOCK

FUNCTION_BLOCK pressure_control
  VAR
    pressure_real : REAL := 2700.0;
  END_VAR
  VAR_INPUT
    pressure : UINT := 58981;
  END_VAR
  VAR
    pressure_sp_real : REAL := 2700.0;
  END_VAR
  VAR_INPUT
    pressure_sp : UINT := 58981;
    curr_pos : UINT := 30000;
  END_VAR
  VAR
    valve_pos_real : REAL := 39.25;
    pos_update_real : REAL := 0.0;
    valve_pos_nominal : REAL := 39.25;
  END_VAR
  VAR_OUTPUT
    valve_pos : UINT := 25886;
  END_VAR
  VAR
    pressure_k : REAL := 20.0;
    pressure_ti : REAL := 999.0;
    cycle_time : TIME := T#50ms;
    scale_to_real5 : scale_to_real;
    scale_to_real4 : scale_to_real;
    scale_to_uint0 : scale_to_uint;
    pressure_max : REAL := 3200.00;
    pressure_min : REAL := 0.0;
    pos_min : REAL := 0.0;
    pos_max : REAL := 100.0;
    scale_to_real0 : scale_to_real;
    _TMP_SUB53_OUT : REAL;
    _TMP_LIMIT55_OUT : REAL;
    _TMP_SUB57_OUT : REAL;
    _TMP_MUL60_OUT : REAL;
  END_VAR

  scale_to_real5(raw_input_value := pressure, real_max := pressure_max, real_min := pressure_min);
  pressure_real := scale_to_real5.scaled_real;
  scale_to_real4(raw_input_value := pressure_sp, real_max := pressure_max, real_min := pressure_min);
  pressure_sp_real := scale_to_real4.scaled_real;
  _TMP_SUB53_OUT := SUB(valve_pos_real, pos_update_real);
  _TMP_LIMIT55_OUT := LIMIT(pos_min, _TMP_SUB53_OUT, pos_max);
  scale_to_uint0(real_in := _TMP_LIMIT55_OUT);
  valve_pos := scale_to_uint0.uint_out;
  scale_to_real0(raw_input_value := curr_pos, real_max := pos_max, real_min := pos_min);
  valve_pos_real := scale_to_real0.scaled_real;
  _TMP_SUB57_OUT := SUB(pressure_sp_real, pressure_real);
  _TMP_MUL60_OUT := MUL(_TMP_SUB57_OUT, pressure_k);
  pos_update_real := _TMP_MUL60_OUT;
END_FUNCTION_BLOCK

FUNCTION_BLOCK pressure_override
  VAR
    pressure_real : REAL := 2700.0;
  END_VAR
  VAR_INPUT
    pressure : UINT := 58981;
    curr_sp : UINT := 58981;
  END_VAR
  VAR
    curr_sp_real : REAL := 2700.0;
    product_sp_real : REAL := 100.0;
    sp_update : REAL := 0.0;
    product_sp_nominl : REAL := 100.0;
  END_VAR
  VAR_OUTPUT
    product_sp : UINT := 13107;
  END_VAR
  VAR
    override_sp_real : REAL := 2900.0;
  END_VAR
  VAR_INPUT
    override_sp : UINT := 63350;
  END_VAR
  VAR
    override_k : REAL := 1.0;
    override_ti : REAL := 99999.0;
    cycle_time : TIME := T#50ms;
    scale_to_real7 : scale_to_real;
    pressure_max : REAL := 3000.0;
    pressure_min : REAL := 0.0;
    flow_max : REAL := 500.0;
    flow_min : REAL := 0.0;
    scale_to_real0 : scale_to_real;
    _TMP_SUB86_OUT : REAL;
    _TMP_MUL87_OUT : REAL;
    _TMP_MAX84_OUT : REAL;
    _TMP_ADD85_OUT : REAL;
    _TMP_LIMIT67_OUT : REAL;
    _TMP_DIV73_OUT : REAL;
    _TMP_MUL75_OUT : REAL;
    _TMP_REAL_TO_UINT79_OUT : UINT;
  END_VAR

  _TMP_SUB86_OUT := SUB(override_sp_real, pressure_real);
  _TMP_MUL87_OUT := MUL(_TMP_SUB86_OUT, override_k);
  _TMP_MAX84_OUT := MAX(_TMP_MUL87_OUT, 0.0);
  sp_update := _TMP_MAX84_OUT;
  scale_to_real7(raw_input_value := pressure, real_max := pressure_max, real_min := pressure_min);
  pressure_real := scale_to_real7.scaled_real;
  scale_to_real0(raw_input_value := curr_sp, real_max := flow_max, real_min := flow_min);
  curr_sp_real := scale_to_real0.scaled_real;
  _TMP_ADD85_OUT := ADD(curr_sp_real, sp_update);
  _TMP_LIMIT67_OUT := LIMIT(50.0, _TMP_ADD85_OUT, 150.0);
  product_sp_real := _TMP_LIMIT67_OUT;
  _TMP_DIV73_OUT := DIV(product_sp_real, 500.0);
  _TMP_MUL75_OUT := MUL(_TMP_DIV73_OUT, 65535.0);
  _TMP_REAL_TO_UINT79_OUT := REAL_TO_UINT(_TMP_MUL75_OUT);
  product_sp := _TMP_REAL_TO_UINT79_OUT;
END_FUNCTION_BLOCK

FUNCTION_BLOCK level_control
  VAR_INPUT
    liquid_level : UINT;
    level_sp : UINT := 30000;
    curr_pos : UINT;
  END_VAR
  VAR_OUTPUT
    new_pos : UINT;
  END_VAR
  VAR
    cycle_time : TIME := T#50ms;
    level_k : REAL := 10.0;
    level_ti : REAL := 99999.0;
    scale_to_real0 : scale_to_real;
    level_max : REAL := 100.0;
    level_min : REAL := 0.0;
    pos_max : REAL := 100.0;
    pos_min : REAL := 0.0;
    level_real : REAL := 44.18;
    pos_real : REAL := 47.0;
    pos_update_real : REAL := 0.0;
    sp_real : REAL := 44.18;
    scale_to_real1 : scale_to_real;
    scale_to_real2 : scale_to_real;
    scale_to_uint0 : scale_to_uint;
    _TMP_SUB32_OUT : REAL;
    _TMP_MUL33_OUT : REAL;
    _TMP_SUB30_OUT : REAL;
    _TMP_LIMIT25_OUT : REAL;
  END_VAR

  scale_to_real0(raw_input_value := liquid_level, real_max := level_max, real_min := level_min);
  level_real := scale_to_real0.scaled_real;
  scale_to_real1(raw_input_value := curr_pos, real_max := pos_max, real_min := pos_min);
  pos_real := scale_to_real1.scaled_real;
  scale_to_real2(raw_input_value := level_sp, real_max := level_max, real_min := level_min);
  sp_real := scale_to_real2.scaled_real;
  _TMP_SUB32_OUT := SUB(sp_real, level_real);
  _TMP_MUL33_OUT := MUL(_TMP_SUB32_OUT, level_k);
  pos_update_real := _TMP_MUL33_OUT;
  _TMP_SUB30_OUT := SUB(pos_real, pos_update_real);
  _TMP_LIMIT25_OUT := LIMIT(pos_min, _TMP_SUB30_OUT, pos_max);
  scale_to_uint0(real_in := _TMP_LIMIT25_OUT);
  new_pos := scale_to_uint0.uint_out;
END_FUNCTION_BLOCK

FUNCTION_BLOCK initialize_sp
  VAR CONSTANT
    flow_sp_c : UINT := 13107;
    a_sp_c : UINT := 65535;
    press_sp_c : UINT := 65535;
    over_sp_c : UINT := 65535;
    level_sp_c : UINT := 65535;
  END_VAR
  VAR_OUTPUT
    flow_sp : UINT;
    a_sp : UINT;
    press_sp : UINT;
    over_sp : UINT;
    level_sp : UINT;
  END_VAR
  VAR
    _TMP_MOVE3_OUT : UINT;
    _TMP_MOVE7_OUT : UINT;
    _TMP_MOVE11_OUT : UINT;
    _TMP_MOVE15_OUT : UINT;
    _TMP_MOVE19_OUT : UINT;
  END_VAR

  _TMP_MOVE3_OUT := MOVE(a_sp_c);
  a_sp := _TMP_MOVE3_OUT;
  _TMP_MOVE7_OUT := MOVE(flow_sp_c);
  flow_sp := _TMP_MOVE7_OUT;
  _TMP_MOVE11_OUT := MOVE(over_sp_c);
  over_sp := _TMP_MOVE11_OUT;
  _TMP_MOVE15_OUT := MOVE(level_sp_c);
  level_sp := _TMP_MOVE15_OUT;
  _TMP_MOVE19_OUT := MOVE(press_sp_c);
  press_sp := _TMP_MOVE19_OUT;
END_FUNCTION_BLOCK

PROGRAM main
  VAR
    flow_control0 : flow_control;
    first_run : BOOL := True;
  END_VAR
  VAR
    flow_set AT %MW0 : UINT;
    a_setpoint AT %MW1 : UINT;
    pressure_sp AT %MW2 : UINT;
    override_sp AT %MW3 : UINT;
    level_sp AT %MW4 : UINT;
  END_VAR
  VAR
    composition_control0 : composition_control;
    scale_to_signed0 : scale_to_signed;
  END_VAR
  VAR
    f1_valve_pos AT %IW0 : UINT;
    f1_flow AT %IW1 : UINT;
    f2_valve_pos AT %IW2 : UINT;
    f2_flow AT %IW3 : UINT;
    purge_valve_pos AT %IW4 : UINT;
    purge_flow AT %IW5 : UINT;
    product_valve_pos AT %IW6 : UINT;
    product_flow AT %IW7 : UINT;
    pressure AT %IW8 : UINT;
    level AT %IW9 : UINT;
    a_in_purge AT %IW10 : UINT;
    b_in_purge AT %IW11 : UINT;
    c_in_purge AT %IW12 : UINT;
    f1_valve_sp AT %QW0 : UINT;
    f2_valve_sp AT %QW1 : UINT;
    purge_valve_sp AT %QW2 : UINT;
    product_valve_sp AT %QW3 : UINT;
  END_VAR
  VAR
    product_valve_safe : UINT := 0;
    purge_valve_safe : UINT := 65535;
    f1_valve_safe : UINT;
    f2_valve_safe : UINT;
    pressure_control0 : pressure_control;
  END_VAR
  VAR
    hmi_pressure AT %MW20 : INT;
    hmi_level AT %MW21 : INT;
    hmi_f1_valve_pos AT %MW22 : INT;
    hmi_f1_flow AT %MW23 : INT;
    hmi_f2_valve_pos AT %MW24 : INT;
    hmi_f2_flow AT %MW25 : INT;
    hmi_purge_valve_pos AT %MW26 : INT;
    hmi_purge_flow AT %MW27 : INT;
    hmi_product_valve_pos AT %MW28 : INT;
    hmi_product_flow AT %MW29 : INT;
    scan_count AT %MW30 : UINT;
  END_VAR
  VAR
    scale_to_signed1 : scale_to_signed;
    scale_to_signed2 : scale_to_signed;
    scale_to_signed3 : scale_to_signed;
    scale_to_signed4 : scale_to_signed;
    scale_to_signed5 : scale_to_signed;
    scale_to_signed6 : scale_to_signed;
    scale_to_signed7 : scale_to_signed;
    scale_to_signed8 : scale_to_signed;
    scale_to_signed9 : scale_to_signed;
    pressure_override0 : pressure_override;
    level_control0 : level_control;
  END_VAR
  VAR_EXTERNAL
    run_bit : BOOL;
  END_VAR
  VAR
    run_bit0 : BOOL := True;
    initialize_sp0 : initialize_sp;
    _TMP_ADD87_OUT : UINT;
    _TMP_GE91_OUT : BOOL;
    _TMP_MOVE92_ENO : BOOL;
    _TMP_MOVE92_OUT : UINT;
  END_VAR

  flow_control0(product_flow := product_flow, curr_pos := f1_valve_pos, flow_set_in := flow_set);
  f1_valve_sp := flow_control0.new_pos;
  composition_control0(a_in_purge := a_in_purge, a_setpoint := a_setpoint, curr_pos := f2_valve_pos);
  f2_valve_sp := composition_control0.new_pos;
  scale_to_signed0(input_uint := pressure);
  hmi_pressure := scale_to_signed0.output_int;
  scale_to_signed1(input_uint := level);
  hmi_level := scale_to_signed1.output_int;
  scale_to_signed2(input_uint := f1_valve_pos);
  hmi_f1_valve_pos := scale_to_signed2.output_int;
  scale_to_signed3(input_uint := f2_valve_pos);
  hmi_f2_valve_pos := scale_to_signed3.output_int;
  scale_to_signed4(input_uint := purge_valve_pos);
  hmi_purge_valve_pos := scale_to_signed4.output_int;
  scale_to_signed5(input_uint := product_valve_pos);
  hmi_product_valve_pos := scale_to_signed5.output_int;
  scale_to_signed6(input_uint := f1_flow);
  hmi_f1_flow := scale_to_signed6.output_int;
  scale_to_signed7(input_uint := f2_flow);
  hmi_f2_flow := scale_to_signed7.output_int;
  scale_to_signed8(input_uint := purge_flow);
  hmi_purge_flow := scale_to_signed8.output_int;
  scale_to_signed9(input_uint := product_flow);
  hmi_product_flow := scale_to_signed9.output_int;
  pressure_control0(pressure := pressure, pressure_sp := pressure_sp, curr_pos := purge_valve_pos);
  purge_valve_sp := pressure_control0.valve_pos;
  pressure_override0(pressure := pressure, curr_sp := flow_set, override_sp := override_sp);
  flow_set := pressure_override0.product_sp;
  level_control0(liquid_level := level, level_sp := level_sp, curr_pos := product_valve_pos);
  product_valve_sp := level_control0.new_pos;
  _TMP_ADD87_OUT := ADD(scan_count, 1);
  scan_count := _TMP_ADD87_OUT;
  _TMP_GE91_OUT := GE(scan_count, 32000);
  _TMP_MOVE92_OUT := MOVE(EN := _TMP_GE91_OUT, IN := 0, ENO => _TMP_MOVE92_ENO);
  IF _TMP_MOVE92_ENO THEN
      scan_count := _TMP_MOVE92_OUT;
  END_IF;
  initialize_sp0(EN := first_run);
  IF initialize_sp0.ENO THEN
    first_run := FALSE; (*reset*)
  END_IF;
  IF initialize_sp0.ENO THEN
      a_setpoint := initialize_sp0.a_sp;
  END_IF;
  IF initialize_sp0.ENO THEN
      flow_set := initialize_sp0.flow_sp;
  END_IF;
  IF initialize_sp0.ENO THEN
      pressure_sp := initialize_sp0.press_sp;
  END_IF;
  IF initialize_sp0.ENO THEN
      override_sp := initialize_sp0.over_sp;
  END_IF;
  IF initialize_sp0.ENO THEN
      level_sp := initialize_sp0.level_sp;
  END_IF;
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    VAR_GLOBAL
      run_bit AT %QX0.0 : BOOL;
    END_VAR
    TASK MainTask(INTERVAL := T#50ms,PRIORITY := 0);
    PROGRAM instance0 WITH MainTask : main;
  END_RESOURCE
END_CONFIGURATION

(*DBG:char md5[] = "65f96e673fa1d29ef754dc8a15f6f958";*)
(*DBG:/**)
(*DBG: * This file is part of OpenPLC Runtime*)
(*DBG: **)
(*DBG: * Copyright (C) 2023 Autonomy, GP Orcullo*)
(*DBG: * Based on the work by GP Orcullo on Beremiz for uC*)
(*DBG: **)
(*DBG: * This program is free software; you can redistribute it and/or*)
(*DBG: * modify it under the terms of the GNU General Public License*)
(*DBG: * as published by the Free Software Foundation; either version 2*)
(*DBG: * of the License, or (at your option) any later version.*)
(*DBG: **)
(*DBG: * This program is distributed in the hope that it will be useful,*)
(*DBG: * but WITHOUT ANY WARRANTY; without even the implied warranty of*)
(*DBG: * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the*)
(*DBG: * GNU General Public License for more details.*)
(*DBG: **)
(*DBG: * You should have received a copy of the GNU General Public License*)
(*DBG: * along with this program; If not, see <http://www.gnu.org/licenses/>.*)
(*DBG: **)
(*DBG: */*)
(*DBG:*)
(*DBG:#include <stdbool.h>*)
(*DBG:*)
(*DBG:#include "iec_types_all.h"*)
(*DBG:#include "POUS.h"*)
(*DBG:*)
(*DBG:#define SAME_ENDIANNESS      0*)
(*DBG:#define REVERSE_ENDIANNESS   1*)
(*DBG:*)
(*DBG:uint8_t endianness;*)
(*DBG:*)
(*DBG:*)
(*DBG:extern __IEC_BOOL_t RES0__RUN_BIT;*)
(*DBG:extern MAIN RES0__INSTANCE0;*)
(*DBG:*)
(*DBG:static const struct {*)
(*DBG:    void *ptr;*)
(*DBG:    __IEC_types_enum type;*)
(*DBG:} debug_vars[] = {*)
(*DBG:    {&(RES0__RUN_BIT), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.FLOW_K), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.FLOW_TI), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.FLOW_TD), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.PRODUCT_FLOW), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.PRODUCT_FLOW_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.CYCLE_TIME), TIME_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.POS_UPDATE_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.CURR_POS_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.NEW_POS), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.CURR_POS), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.FLOW_SET_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.FLOW_SET_IN), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL0.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL0.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL0.RAW_INPUT_VALUE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL0.SCALED_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL0.REAL_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL0.REAL_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL0.RAW_MAX), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL0.RAW_MIN), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL0.RATE), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL0.OFFSET), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL1.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL1.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL1.RAW_INPUT_VALUE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL1.SCALED_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL1.REAL_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL1.REAL_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL1.RAW_MAX), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL1.RAW_MIN), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL1.RATE), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL1.OFFSET), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.FLOW_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.FLOW_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.POS_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.POS_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL2.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL2.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL2.RAW_INPUT_VALUE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL2.SCALED_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL2.REAL_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL2.REAL_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL2.RAW_MAX), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL2.RAW_MIN), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL2.RATE), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_REAL2.OFFSET), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_UINT0.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_UINT0.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_UINT0.REAL_IN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_UINT0.UINT_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_UINT0._TMP_DIV1_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_UINT0._TMP_MUL4_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0.SCALE_TO_UINT0._TMP_REAL_TO_UINT6_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0._TMP_SUB59_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0._TMP_MUL60_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0._TMP_ADD58_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_CONTROL0._TMP_LIMIT40_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FIRST_RUN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.FLOW_SET), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.A_SETPOINT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_SP), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.OVERRIDE_SP), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_SP), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.A_IN_PURGE_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.A_IN_PURGE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.A_SETPOINT_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.A_SETPOINT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.CURR_POS), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.VALVE_POS_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.POS_UPDATE_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.VALVE_POS_NOMINAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.NEW_POS), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.COMPOSITION_K), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.COMPOSITION_TI), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.CYCLE_TIME), TIME_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL3.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL3.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL3.RAW_INPUT_VALUE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL3.SCALED_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL3.REAL_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL3.REAL_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL3.RAW_MAX), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL3.RAW_MIN), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL3.RATE), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL3.OFFSET), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL2.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL2.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL2.RAW_INPUT_VALUE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL2.SCALED_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL2.REAL_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL2.REAL_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL2.RAW_MAX), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL2.RAW_MIN), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL2.RATE), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL2.OFFSET), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_UINT0.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_UINT0.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_UINT0.REAL_IN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_UINT0.UINT_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_UINT0._TMP_DIV1_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_UINT0._TMP_MUL4_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_UINT0._TMP_REAL_TO_UINT6_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.COMP_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.COMP_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.POS_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.POS_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL0.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL0.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL0.RAW_INPUT_VALUE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL0.SCALED_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL0.REAL_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL0.REAL_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL0.RAW_MAX), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL0.RAW_MIN), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL0.RATE), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0.SCALE_TO_REAL0.OFFSET), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0._TMP_SUB45_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0._TMP_MUL46_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0._TMP_ADD42_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COMPOSITION_CONTROL0._TMP_LIMIT44_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED0.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED0.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED0.INPUT_UINT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED0.OUTPUT_INT), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED0._TMP_DIV3_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED0._TMP_ABS8_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED0._TMP_UINT_TO_INT9_OUT), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.F1_VALVE_POS), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.F1_FLOW), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.F2_VALVE_POS), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.F2_FLOW), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PURGE_VALVE_POS), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PURGE_FLOW), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRODUCT_VALVE_POS), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRODUCT_FLOW), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.A_IN_PURGE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.B_IN_PURGE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.C_IN_PURGE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.F1_VALVE_SP), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.F2_VALVE_SP), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PURGE_VALVE_SP), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRODUCT_VALVE_SP), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRODUCT_VALVE_SAFE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PURGE_VALVE_SAFE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.F1_VALVE_SAFE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.F2_VALVE_SAFE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.PRESSURE_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.PRESSURE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.PRESSURE_SP_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.PRESSURE_SP), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.CURR_POS), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.VALVE_POS_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.POS_UPDATE_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.VALVE_POS_NOMINAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.VALVE_POS), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.PRESSURE_K), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.PRESSURE_TI), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.CYCLE_TIME), TIME_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL5.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL5.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL5.RAW_INPUT_VALUE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL5.SCALED_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL5.REAL_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL5.REAL_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL5.RAW_MAX), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL5.RAW_MIN), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL5.RATE), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL5.OFFSET), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL4.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL4.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL4.RAW_INPUT_VALUE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL4.SCALED_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL4.REAL_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL4.REAL_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL4.RAW_MAX), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL4.RAW_MIN), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL4.RATE), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL4.OFFSET), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_UINT0.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_UINT0.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_UINT0.REAL_IN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_UINT0.UINT_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_UINT0._TMP_DIV1_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_UINT0._TMP_MUL4_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_UINT0._TMP_REAL_TO_UINT6_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.PRESSURE_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.PRESSURE_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.POS_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.POS_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL0.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL0.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL0.RAW_INPUT_VALUE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL0.SCALED_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL0.REAL_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL0.REAL_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL0.RAW_MAX), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL0.RAW_MIN), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL0.RATE), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0.SCALE_TO_REAL0.OFFSET), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0._TMP_SUB53_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0._TMP_LIMIT55_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0._TMP_SUB57_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_CONTROL0._TMP_MUL60_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.HMI_PRESSURE), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.HMI_LEVEL), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.HMI_F1_VALVE_POS), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.HMI_F1_FLOW), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.HMI_F2_VALVE_POS), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.HMI_F2_FLOW), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.HMI_PURGE_VALVE_POS), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.HMI_PURGE_FLOW), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.HMI_PRODUCT_VALVE_POS), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.HMI_PRODUCT_FLOW), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCAN_COUNT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED1.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED1.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED1.INPUT_UINT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED1.OUTPUT_INT), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED1._TMP_DIV3_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED1._TMP_ABS8_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED1._TMP_UINT_TO_INT9_OUT), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED2.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED2.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED2.INPUT_UINT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED2.OUTPUT_INT), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED2._TMP_DIV3_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED2._TMP_ABS8_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED2._TMP_UINT_TO_INT9_OUT), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED3.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED3.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED3.INPUT_UINT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED3.OUTPUT_INT), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED3._TMP_DIV3_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED3._TMP_ABS8_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED3._TMP_UINT_TO_INT9_OUT), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED4.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED4.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED4.INPUT_UINT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED4.OUTPUT_INT), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED4._TMP_DIV3_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED4._TMP_ABS8_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED4._TMP_UINT_TO_INT9_OUT), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED5.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED5.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED5.INPUT_UINT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED5.OUTPUT_INT), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED5._TMP_DIV3_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED5._TMP_ABS8_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED5._TMP_UINT_TO_INT9_OUT), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED6.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED6.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED6.INPUT_UINT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED6.OUTPUT_INT), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED6._TMP_DIV3_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED6._TMP_ABS8_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED6._TMP_UINT_TO_INT9_OUT), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED7.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED7.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED7.INPUT_UINT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED7.OUTPUT_INT), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED7._TMP_DIV3_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED7._TMP_ABS8_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED7._TMP_UINT_TO_INT9_OUT), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED8.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED8.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED8.INPUT_UINT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED8.OUTPUT_INT), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED8._TMP_DIV3_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED8._TMP_ABS8_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED8._TMP_UINT_TO_INT9_OUT), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED9.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED9.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED9.INPUT_UINT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED9.OUTPUT_INT), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED9._TMP_DIV3_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED9._TMP_ABS8_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SCALE_TO_SIGNED9._TMP_UINT_TO_INT9_OUT), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.PRESSURE_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.PRESSURE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.CURR_SP), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.CURR_SP_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.PRODUCT_SP_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SP_UPDATE), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.PRODUCT_SP_NOMINL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.PRODUCT_SP), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.OVERRIDE_SP_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.OVERRIDE_SP), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.OVERRIDE_K), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.OVERRIDE_TI), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.CYCLE_TIME), TIME_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SCALE_TO_REAL7.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SCALE_TO_REAL7.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SCALE_TO_REAL7.RAW_INPUT_VALUE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SCALE_TO_REAL7.SCALED_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SCALE_TO_REAL7.REAL_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SCALE_TO_REAL7.REAL_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SCALE_TO_REAL7.RAW_MAX), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SCALE_TO_REAL7.RAW_MIN), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SCALE_TO_REAL7.RATE), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SCALE_TO_REAL7.OFFSET), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.PRESSURE_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.PRESSURE_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.FLOW_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.FLOW_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SCALE_TO_REAL0.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SCALE_TO_REAL0.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SCALE_TO_REAL0.RAW_INPUT_VALUE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SCALE_TO_REAL0.SCALED_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SCALE_TO_REAL0.REAL_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SCALE_TO_REAL0.REAL_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SCALE_TO_REAL0.RAW_MAX), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SCALE_TO_REAL0.RAW_MIN), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SCALE_TO_REAL0.RATE), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0.SCALE_TO_REAL0.OFFSET), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0._TMP_SUB86_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0._TMP_MUL87_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0._TMP_MAX84_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0._TMP_ADD85_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0._TMP_LIMIT67_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0._TMP_DIV73_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0._TMP_MUL75_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PRESSURE_OVERRIDE0._TMP_REAL_TO_UINT79_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.LIQUID_LEVEL), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.LEVEL_SP), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.CURR_POS), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.NEW_POS), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.CYCLE_TIME), TIME_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.LEVEL_K), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.LEVEL_TI), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL0.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL0.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL0.RAW_INPUT_VALUE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL0.SCALED_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL0.REAL_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL0.REAL_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL0.RAW_MAX), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL0.RAW_MIN), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL0.RATE), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL0.OFFSET), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.LEVEL_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.LEVEL_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.POS_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.POS_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.LEVEL_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.POS_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.POS_UPDATE_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SP_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL1.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL1.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL1.RAW_INPUT_VALUE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL1.SCALED_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL1.REAL_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL1.REAL_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL1.RAW_MAX), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL1.RAW_MIN), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL1.RATE), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL1.OFFSET), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL2.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL2.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL2.RAW_INPUT_VALUE), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL2.SCALED_REAL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL2.REAL_MAX), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL2.REAL_MIN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL2.RAW_MAX), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL2.RAW_MIN), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL2.RATE), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_REAL2.OFFSET), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_UINT0.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_UINT0.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_UINT0.REAL_IN), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_UINT0.UINT_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_UINT0._TMP_DIV1_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_UINT0._TMP_MUL4_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0.SCALE_TO_UINT0._TMP_REAL_TO_UINT6_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0._TMP_SUB32_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0._TMP_MUL33_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0._TMP_SUB30_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.LEVEL_CONTROL0._TMP_LIMIT25_OUT), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.RUN_BIT), BOOL_P_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.RUN_BIT0), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.INITIALIZE_SP0.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.INITIALIZE_SP0.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.INITIALIZE_SP0.FLOW_SP_C), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.INITIALIZE_SP0.A_SP_C), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.INITIALIZE_SP0.PRESS_SP_C), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.INITIALIZE_SP0.OVER_SP_C), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.INITIALIZE_SP0.LEVEL_SP_C), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.INITIALIZE_SP0.FLOW_SP), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.INITIALIZE_SP0.A_SP), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.INITIALIZE_SP0.PRESS_SP), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.INITIALIZE_SP0.OVER_SP), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.INITIALIZE_SP0.LEVEL_SP), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.INITIALIZE_SP0._TMP_MOVE3_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.INITIALIZE_SP0._TMP_MOVE7_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.INITIALIZE_SP0._TMP_MOVE11_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.INITIALIZE_SP0._TMP_MOVE15_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.INITIALIZE_SP0._TMP_MOVE19_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0._TMP_ADD87_OUT), UINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0._TMP_GE91_OUT), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0._TMP_MOVE92_ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0._TMP_MOVE92_OUT), UINT_ENUM},*)
(*DBG:};*)
(*DBG:*)
(*DBG:#define VAR_COUNT               414*)
(*DBG:*)
(*DBG:uint16_t get_var_count(void)*)
(*DBG:{*)
(*DBG:    return VAR_COUNT;*)
(*DBG:}*)
(*DBG:*)
(*DBG:size_t get_var_size(size_t idx)*)
(*DBG:{*)
(*DBG:    if (idx >= VAR_COUNT)*)
(*DBG:    {*)
(*DBG:        return 0;*)
(*DBG:    }*)
(*DBG:    switch (debug_vars[idx].type) {*)
(*DBG:    case REAL_ENUM:*)
(*DBG:        return sizeof(REAL);*)
(*DBG:    case INT_ENUM:*)
(*DBG:        return sizeof(INT);*)
(*DBG:    case BOOL_ENUM:*)
(*DBG:    case BOOL_P_ENUM:*)
(*DBG:        return sizeof(BOOL);*)
(*DBG:    case TIME_ENUM:*)
(*DBG:        return sizeof(TIME);*)
(*DBG:    case UINT_ENUM:*)
(*DBG:        return sizeof(UINT);*)
(*DBG:    default:*)
(*DBG:        return 0;*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)
(*DBG:void *get_var_addr(size_t idx)*)
(*DBG:{*)
(*DBG:    void *ptr = debug_vars[idx].ptr;*)
(*DBG:*)
(*DBG:    switch (debug_vars[idx].type) {*)
(*DBG:    case REAL_ENUM:*)
(*DBG:        return (void *)&((__IEC_REAL_t *) ptr)->value;*)
(*DBG:    case INT_ENUM:*)
(*DBG:        return (void *)&((__IEC_INT_t *) ptr)->value;*)
(*DBG:    case BOOL_ENUM:*)
(*DBG:        return (void *)&((__IEC_BOOL_t *) ptr)->value;*)
(*DBG:    case BOOL_P_ENUM:*)
(*DBG:        return (void *)((((__IEC_BOOL_p *) ptr)->flags & __IEC_FORCE_FLAG) *)
(*DBG:                        ? &(((__IEC_BOOL_p *) ptr)->fvalue) *)
(*DBG:                        : ((__IEC_BOOL_p *) ptr)->value);*)
(*DBG:    case TIME_ENUM:*)
(*DBG:        return (void *)&((__IEC_TIME_t *) ptr)->value;*)
(*DBG:    case UINT_ENUM:*)
(*DBG:        return (void *)&((__IEC_UINT_t *) ptr)->value;*)
(*DBG:    default:*)
(*DBG:        return 0;*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)
(*DBG:void force_var(size_t idx, bool forced, void *val)*)
(*DBG:{*)
(*DBG:    void *ptr = debug_vars[idx].ptr;*)
(*DBG:*)
(*DBG:    if (forced) {*)
(*DBG:        size_t var_size = get_var_size(idx);*)
(*DBG:        switch (debug_vars[idx].type) {*)
(*DBG:        case REAL_ENUM: {*)
(*DBG:            memcpy(&((__IEC_REAL_t *) ptr)->value, val, var_size);*)
(*DBG:            //((__IEC_REAL_t *) ptr)->value = *((REAL *) val);*)
(*DBG:            ((__IEC_REAL_t *) ptr)->flags |= __IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        }*)
(*DBG:        case INT_ENUM: {*)
(*DBG:            memcpy(&((__IEC_INT_t *) ptr)->value, val, var_size);*)
(*DBG:            //((__IEC_INT_t *) ptr)->value = *((INT *) val);*)
(*DBG:            ((__IEC_INT_t *) ptr)->flags |= __IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        }*)
(*DBG:        case BOOL_ENUM: {*)
(*DBG:            memcpy(&((__IEC_BOOL_t *) ptr)->value, val, var_size);*)
(*DBG:            //((__IEC_BOOL_t *) ptr)->value = *((BOOL *) val);*)
(*DBG:            ((__IEC_BOOL_t *) ptr)->flags |= __IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        }*)
(*DBG:        case BOOL_P_ENUM: {*)
(*DBG:            memcpy(&((__IEC_BOOL_p *) ptr)->fvalue, val, var_size);*)
(*DBG:            //((__IEC_BOOL_p *) ptr)->fvalue = *((BOOL *) val);*)
(*DBG:            ((__IEC_BOOL_p *) ptr)->flags |= __IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        }*)
(*DBG:        case TIME_ENUM: {*)
(*DBG:            memcpy(&((__IEC_TIME_t *) ptr)->value, val, var_size);*)
(*DBG:            //((__IEC_TIME_t *) ptr)->value = *((TIME *) val);*)
(*DBG:            ((__IEC_TIME_t *) ptr)->flags |= __IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        }*)
(*DBG:        case UINT_ENUM: {*)
(*DBG:            memcpy(&((__IEC_UINT_t *) ptr)->value, val, var_size);*)
(*DBG:            //((__IEC_UINT_t *) ptr)->value = *((UINT *) val);*)
(*DBG:            ((__IEC_UINT_t *) ptr)->flags |= __IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        }*)
(*DBG:        default:*)
(*DBG:            break;*)
(*DBG:        }*)
(*DBG:    } else {*)
(*DBG:        switch (debug_vars[idx].type) {*)
(*DBG:        case REAL_ENUM:*)
(*DBG:            ((__IEC_REAL_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        case INT_ENUM:*)
(*DBG:            ((__IEC_INT_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        case BOOL_ENUM:*)
(*DBG:            ((__IEC_BOOL_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        case BOOL_P_ENUM:*)
(*DBG:            ((__IEC_BOOL_p *) ptr)->flags &= ~__IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        case TIME_ENUM:*)
(*DBG:            ((__IEC_TIME_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        case UINT_ENUM:*)
(*DBG:            ((__IEC_UINT_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        default:*)
(*DBG:            break;*)
(*DBG:        }*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)
(*DBG:void swap_bytes(void *ptr, size_t size) *)
(*DBG:{*)
(*DBG:    uint8_t *bytePtr = (uint8_t *)ptr;*)
(*DBG:    size_t i;*)
(*DBG:    for (i = 0; i < size / 2; ++i) *)
(*DBG:    {*)
(*DBG:        uint8_t temp = bytePtr[i];*)
(*DBG:        bytePtr[i] = bytePtr[size - 1 - i];*)
(*DBG:        bytePtr[size - 1 - i] = temp;*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)
(*DBG:void trace_reset(void)*)
(*DBG:{*)
(*DBG:    for (size_t i=0; i < VAR_COUNT; i++) *)
(*DBG:    {*)
(*DBG:        force_var(i, false, 0);*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)
(*DBG:void set_trace(size_t idx, bool forced, void *val)*)
(*DBG:{*)
(*DBG:    if (idx >= 0 && idx < VAR_COUNT) *)
(*DBG:    {*)
(*DBG:        if (endianness == REVERSE_ENDIANNESS)*)
(*DBG:        {*)
(*DBG:            // Aaaaarghhhh... Stupid AVR is Big Endian.*)
(*DBG:            swap_bytes(val, get_var_size(idx));*)
(*DBG:        }*)
(*DBG:*)
(*DBG:        force_var(idx, forced, val);*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)
(*DBG:void set_endianness(uint8_t value)*)
(*DBG:{*)
(*DBG:    if (value == SAME_ENDIANNESS || value == REVERSE_ENDIANNESS)*)
(*DBG:    {*)
(*DBG:        endianness = value;*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)