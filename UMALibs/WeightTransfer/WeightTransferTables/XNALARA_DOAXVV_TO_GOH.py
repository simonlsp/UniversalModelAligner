TransferTable = [
        [["Armature"], [("GFA_MWT_SKE_Body", 1.0)]],
        [["root ground"], [("GFA_MWT_SKE_Body", 1.0)]],
        [["root hips"], [("GFA_MWT_SKE_Body", 1.0)]],
        [["pelvis"], [("GFA_MWT_SKE_Body", 1.0)]],

        [["leg right butt base"], [("GFA_MWT_SKE_Body", 0.75), ("GFA_MWT_SKE_foot1R", 0.25)]],
        [["leg right thigh"], [("GFA_MWT_SKE_foot1R", 1.0)]],
        [["leg right knee"], [("GFA_MWT_SKE_foot2R", 1.0)]],
        [["leg right ankle"], [("GFA_MWT_SKE_foot2R", 0.5), ("GFA_MWT_SKE_foot3R", 0.5)]],
        [["leg right toes"], [("GFA_MWT_SKE_foot2R", 1.0)]],

        [["leg left butt base"], [("GFA_MWT_SKE_Body", 0.75), ("GFA_MWT_SKE_foot1L", 0.25)]],
        [["leg left thigh"], [("GFA_MWT_SKE_foot1L", 1.0)]],
        [["leg left knee"], [("GFA_MWT_SKE_foot2L", 1.0)]],
        [["leg left ankle"], [("GFA_MWT_SKE_foot2L", 0.5), ("GFA_MWT_SKE_foot3L", 0.5)]],
        [["leg left toes"], [("GFA_MWT_SKE_foot2L", 1.0)]],

        [["spine lower"], [("GFA_MWT_SKE_Body", 0.5), ("GFA_MWT_SKE_IK_UpDown", 0.5)]],
        [["spine upper"], [("GFA_MWT_SKE_IK_UpDown", 1.0)]],

        [["head neck lower"], [("GFA_MWT_SKE_Head", 1.0)]],
        [["head neck upper"], [("GFA_MWT_SKE_Head", 1.0)]],

        [["arm left shoulder 1"], [("GFA_MWT_SKE_IK_UpDown", 0.67), ("GFA_MWT_SKE_Hand1L", 0.33)]],
        [["arm right shoulder 1"], [("GFA_MWT_SKE_IK_UpDown", 0.67), ("GFA_MWT_SKE_Hand1R", 0.33)]],

        [["arm left shoulder 2"], [("GFA_MWT_SKE_Hand1L", 1.0)]],
        [["arm right shoulder 2"], [("GFA_MWT_SKE_Hand1R", 1.0)]],

        [["arm left elbow"], [("GFA_MWT_SKE_Hand2L", 1.0)]],
        [["arm right elbow"], [("GFA_MWT_SKE_Hand2R", 1.0)]],

        [["arm left wrist"], [("GFA_MWT_SKE_Palm1L", 0.85), ("GFA_MWT_SKE_Palm1L", 0.15)]], # Is this correct???
        [["arm left finger 1a"], [("GFA_MWT_SKE_Palm1L", 0.975), ("GFA_MWT_SKE_Palm1L", 0.025)]],
        [["arm left finger 1b"], [("GFA_MWT_SKE_Palm1L", 0.95), ("GFA_MWT_SKE_Palm1L", 0.05)]],
        [["arm left finger 1c"], [("GFA_MWT_SKE_Palm1L", 0.9), ("GFA_MWT_SKE_Palm2L", 0.1)]],

        [["arm left finger 2a"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.425), ("GFA_MWT_SKE_Palm3L", 0.075)]],
        [["arm left finger 3a"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.425), ("GFA_MWT_SKE_Palm3L", 0.075)]],
        [["arm left finger 4a"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.425), ("GFA_MWT_SKE_Palm3L", 0.075)]],
        [["arm left finger 5a"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.425), ("GFA_MWT_SKE_Palm3L", 0.075)]],

        [["arm left finger 2b"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.35), ("GFA_MWT_SKE_Palm3L", 0.15)]],
        [["arm left finger 3b"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.35), ("GFA_MWT_SKE_Palm3L", 0.15)]],
        [["arm left finger 4b"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.35), ("GFA_MWT_SKE_Palm3L", 0.15)]],
        [["arm left finger 5b"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.35), ("GFA_MWT_SKE_Palm3L", 0.15)]],

        [["arm left finger 2c"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.36), ("GFA_MWT_SKE_Palm3L", 0.14)]],
        [["arm left finger 3c"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.37), ("GFA_MWT_SKE_Palm3L", 0.13)]],
        [["arm left finger 4c"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.38), ("GFA_MWT_SKE_Palm3L", 0.12)]],
        [["arm left finger 5c"], [("GFA_MWT_SKE_Palm1L", 0.50), ("GFA_MWT_SKE_Palm2L", 0.39), ("GFA_MWT_SKE_Palm3L", 0.11)]],

        [["arm right wrist"], [("GFA_MWT_SKE_Palm1R", 0.85), ("GFA_MWT_SKE_Palm1R", 0.15)]], # Is this correct???
        [["arm right finger 1a"], [("GFA_MWT_SKE_Palm1R", 0.975), ("GFA_MWT_SKE_Palm1R", 0.025)]],
        [["arm right finger 1b"], [("GFA_MWT_SKE_Palm1R", 0.95), ("GFA_MWT_SKE_Palm1R", 0.05)]],
        [["arm right finger 1c"], [("GFA_MWT_SKE_Palm1R", 0.9), ("GFA_MWT_SKE_Palm2R", 0.1)]],

        [["arm right finger 2a"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.425), ("GFA_MWT_SKE_Palm2R", 0.075)]],
        [["arm right finger 3a"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.425), ("GFA_MWT_SKE_Palm2R", 0.075)]],
        [["arm right finger 4a"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.425), ("GFA_MWT_SKE_Palm2R", 0.075)]],
        [["arm right finger 5a"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.425), ("GFA_MWT_SKE_Palm2R", 0.075)]],

        [["arm right finger 2b"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.35), ("GFA_MWT_SKE_Palm3R", 0.15)]],
        [["arm right finger 3b"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.35), ("GFA_MWT_SKE_Palm3R", 0.15)]],
        [["arm right finger 4b"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.35), ("GFA_MWT_SKE_Palm3R", 0.15)]],
        [["arm right finger 5b"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.35), ("GFA_MWT_SKE_Palm3R", 0.15)]],
        
        [["arm right finger 2c"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.36), ("GFA_MWT_SKE_Palm3R", 0.14)]],
        [["arm right finger 3c"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.37), ("GFA_MWT_SKE_Palm3R", 0.13)]],
        [["arm right finger 4c"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.38), ("GFA_MWT_SKE_Palm3R", 0.12)]],
        [["arm right finger 5c"], [("GFA_MWT_SKE_Palm1R", 0.50), ("GFA_MWT_SKE_Palm2R", 0.39), ("GFA_MWT_SKE_Palm3R", 0.11)]],
        
    ]