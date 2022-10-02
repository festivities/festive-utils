// allow Final IK to work in Editor Mode
// yoinked from https://groups.google.com/g/final-ik/c/w9MKR-Flg7M

using UnityEngine;
using System.Collections;
using RootMotion.FinalIK;

[ExecuteInEditMode]
public class EditorIK : MonoBehaviour {
    
    private IK ik;

    void Start() { 
        ik = GetComponent<IK>();
        ik.GetIKSolver().Initiate(ik.transform);
    }
    
    void Update() {
        // Fix Transforms (reset pose) otherwise IK will solve additively on top of itself frame by frame if no animation is playing to overwrite it
        if (ik.fixTransforms) ik.GetIKSolver().FixTransforms();

        // If you need to sample animation, do it here

        // Update IK
        ik.GetIKSolver().Update();
    }
}
