TransferTable = [
    [["ControlNode"], [("GFA_MWT_SKE_Body", 1.0)]],
    [["ParentNode"], [("GFA_MWT_SKE_Body", 1.0)]],
    [["Center"], [("GFA_MWT_SKE_Body", 1.0)]],
    [["Groove"], [("GFA_MWT_SKE_Body", 1.0)]],
    [["_shadow_WaistCancel_L"], [("GFA_MWT_SKE_Body", 1.0)]],
    [["_shadow_WaistCancel_R"], [("GFA_MWT_SKE_Body", 1.0)]],

    [["Waist"], [("GFA_MWT_SKE_Body", 1.0)]],

    [["LowerBody"], [("GFA_MWT_SKE_Body", 1.0)]],

    [["WaistCancel_R"], [("GFA_MWT_SKE_foot1R", 1.0)]], # ??????
    [["Leg_R"], [("GFA_MWT_SKE_foot1R", 1.0)]],
    [["Knee_R"], [("GFA_MWT_SKE_foot2R", 1.0)]],
    [["Ankle_R"], [("GFA_MWT_SKE_foot2R", 0.5), ("GFA_MWT_SKE_foot3R", 0.5)]],
    [["AnkleTip_R"], [("GFA_MWT_SKE_foot2R", 0.5), ("GFA_MWT_SKE_foot3R", 0.5)]],
    [["LegTipEX_R"], [("GFA_MWT_SKE_foot2R", 0.5), ("GFA_MWT_SKE_foot3R", 0.5)]],

    [["WaistCancel_L"], [("GFA_MWT_SKE_foot1L", 1.0)]], # ??????
    [["Leg_L"], [("GFA_MWT_SKE_foot1L", 1.0)]],
    [["Knee_L"], [("GFA_MWT_SKE_foot2L", 1.0)]],
    [["Ankle_L"], [("GFA_MWT_SKE_foot2L", 0.5), ("GFA_MWT_SKE_foot3L", 0.5)]],
    [["AnkleTip_L"], [("GFA_MWT_SKE_foot2L", 0.5), ("GFA_MWT_SKE_foot3L", 0.5)]],
    [["LegTipEX_L"], [("GFA_MWT_SKE_foot2L", 0.5), ("GFA_MWT_SKE_foot3L", 0.5)]],

    [["UpperBody"], [("GFA_MWT_SKE_IK_LeftRight", 1.0)]],
    [["UpperBody2"], [("GFA_MWT_SKE_IK_UpDown", 1.0)]],


    [["ShoulderP_L"], [("GFA_MWT_SKE_Clavicle_left", 1.0)]],
    [["Shoulder_L"], [("GFA_MWT_SKE_Clavicle_left", 1.0)]],
    [["ShoulderP_R"], [("GFA_MWT_SKE_Clavicle_right", 1.0)]],
    [["Shoulder_R"], [("GFA_MWT_SKE_Clavicle_right", 1.0)]],

    [["ShoulderC_L"], [("GFA_MWT_SKE_Hand1L", 1.0)]],
    [["Arm_L"], [("GFA_MWT_SKE_Hand1L", 1.0)]],
    [["ArmTwist_L"], [("GFA_MWT_SKE_Hand1L", 1.0)]],
    [["ShoulderC_R"], [("GFA_MWT_SKE_Hand1R", 1.0)]],
    [["Arm_R"], [("GFA_MWT_SKE_Hand1R", 1.0)]],
    [["ArmTwist_R"], [("GFA_MWT_SKE_Hand1R", 1.0)]],

    [["Elbow_L"], [("GFA_MWT_SKE_Hand2L", 1.0)]],
    [["HandTwist_L"], [("GFA_MWT_SKE_Hand2L", 0.9), ("GFA_MWT_SKE_Palm1L", 0.1)]], # Is this correct???
    [["Elbow_R"], [("GFA_MWT_SKE_Hand2R", 1.0)]],
    [["HandTwist_R"], [("GFA_MWT_SKE_Hand2R", 0.9), ("GFA_MWT_SKE_Palm1R", 0.1)]], # Is this correct???

    [["Neck"], [("GFA_MWT_SKE_Head", 1.0)]],
    [["Head"], [("GFA_MWT_SKE_Head", 1.0)]],
    [["Eye_L"], [("GFA_MWT_SKE_Head", 1.0)]],
    [["Eye_R"], [("GFA_MWT_SKE_Head", 1.0)]],


    [["Wrist_L"], [("GFA_MWT_SKE_Palm1L", 1.0)]], # Is this correct???
    [["Thumb0_L"], [("GFA_MWT_SKE_Palm1L", 0.975), ("GFA_MWT_SKE_Palm1L", 0.025)]],
    [["Thumb1_L"], [("GFA_MWT_SKE_Palm1L", 0.95), ("GFA_MWT_SKE_Palm1L", 0.05)]],
    [["Thumb2_L"], [("GFA_MWT_SKE_Palm1L", 0.9), ("GFA_MWT_SKE_Palm2L", 0.1)]],

    [["IndexFinger1_L"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.425), ("GFA_MWT_SKE_Palm3L", 0.075)]],
    [["MiddleFinger1_L"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.425), ("GFA_MWT_SKE_Palm3L", 0.075)]],
    [["RingFinger1_L"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.425), ("GFA_MWT_SKE_Palm3L", 0.075)]],
    [["LittleFinger1_L"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.425), ("GFA_MWT_SKE_Palm3L", 0.075)]],

    [["IndexFinger2_L"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.35), ("GFA_MWT_SKE_Palm3L", 0.15)]],
    [["MiddleFinger2_L"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.35), ("GFA_MWT_SKE_Palm3L", 0.15)]],
    [["RingFinger2_L"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.35), ("GFA_MWT_SKE_Palm3L", 0.15)]],
    [["LittleFinger2_L"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.35), ("GFA_MWT_SKE_Palm3L", 0.15)]],

    [["IndexFinger3_L"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.36), ("GFA_MWT_SKE_Palm3L", 0.14)]],
    [["MiddleFinger3_L"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.37), ("GFA_MWT_SKE_Palm3L", 0.13)]],
    [["RingFinger3_L"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.38), ("GFA_MWT_SKE_Palm3L", 0.12)]],
    [["LittleFinger3_L"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.39), ("GFA_MWT_SKE_Palm3L", 0.11)]],

    [["Wrist_R"], [("GFA_MWT_SKE_Palm1R", 1.0)]], # Is this correct???
    [["Thumb0_R"], [("GFA_MWT_SKE_Palm1R", 0.975), ("GFA_MWT_SKE_Palm1R", 0.025)]],
    [["Thumb1_R"], [("GFA_MWT_SKE_Palm1R", 0.95), ("GFA_MWT_SKE_Palm1R", 0.05)]],
    [["Thumb2_R"], [("GFA_MWT_SKE_Palm1R", 0.9), ("GFA_MWT_SKE_Palm2R", 0.1)]],

    [["IndexFinger1_R"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.425), ("GFA_MWT_SKE_Palm2R", 0.075)]],
    [["MiddleFinger1_R"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.425), ("GFA_MWT_SKE_Palm2R", 0.075)]],
    [["RingFinger1_R"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.425), ("GFA_MWT_SKE_Palm2R", 0.075)]],
    [["LittleFinger1_R"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.425), ("GFA_MWT_SKE_Palm2R", 0.075)]],

    [["IndexFinger2_R"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.35), ("GFA_MWT_SKE_Palm3R", 0.15)]],
    [["MiddleFinger2_R"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.35), ("GFA_MWT_SKE_Palm3R", 0.15)]],
    [["RingFinger2_R"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.35), ("GFA_MWT_SKE_Palm3R", 0.15)]],
    [["LittleFinger2_R"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.35), ("GFA_MWT_SKE_Palm3R", 0.15)]],
    
    [["IndexFinger3_R"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.36), ("GFA_MWT_SKE_Palm3R", 0.14)]],
    [["MiddleFinger3_R"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.37), ("GFA_MWT_SKE_Palm3R", 0.13)]],
    [["RingFinger3_R"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.38), ("GFA_MWT_SKE_Palm3R", 0.12)]],
    [["LittleFinger3_R"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.39), ("GFA_MWT_SKE_Palm3R", 0.11)]],
    
]