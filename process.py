import subprocess, os
import sys

'''
    The code to run the workflow code on a sample
'''


def execute_script(cmd_line):
    """execute script inside program"""
    
    process = subprocess.Popen(cmd_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Poll process for new output until finished
    while True:
        nextline = process.stdout.readline()
        if nextline == '' and process.poll() is not None:
            break
        sys.stdout.write(nextline)
        sys.stdout.flush()

    output = process.communicate()[0]
    exitCode = process.returncode

    if (exitCode == 0):
        return output
    else:
        raise ProcessException(cmd_line, exitCode, output)
        
        
def process_sample(name,current_path,args):
    '''
        Process a sample within the collection.

        This function is run within the singularity container defined in
        the WORKFLOW_CONFIG using the python3 interpreter.

        Args:
            name (str): name of the sample
            path (str): path to the sample file(s)
            args (dict): workflow parameters

        Returns:
            A python dictionary with any/all of the following keys:

            'key-val': a dictionary of key value pairs. These are accumulated
                from all the process_sample calls and placed in a csv file.
                Values must be primitives (float,int,string).

                Keys do not need to be the same across all samples. Keys missing
                from samples are set to NULL in the resulting csv file.

            'files': a list of paths to the files to include in the results.
                The files are placed in a "files" folder and compressed.

                The paths must be relative to the sample directory, which is the
                current directory when this script is called.

                Files names do not need to be unique between samples.
    '''
    
    settings = args['settings']['params']
    
    # step 1 : Region of Interest extraction
    ROI_seg = "python /opt/code/bbox_seg.py -p " + current_path + "/" + " -ft " + str(settings['filetype'])
    
    print("Extracting Region of Interest from input images...\n")
    
    execute_script(ROI_seg)

    
    
    # step 2 : gamma_correction 
    #gamma_correction = "python /opt/code/gamma_correction.py -p " + current_path + "segmented/" 
    
    #print("Luminance enhancement by gamma_correction method...\n")
    
    #execute_script(gamma_correction)
    
    
    
    # step 3: compute 3D model from preprocessed image set
    compute_3d_model = "/opt/code/vsfm/bin/VisualSFM sfm+pmvs " + current_path + "/segmented/" 
    
    execute_script(compute_3d_model)
    
    
     
    return {'files':[ current_path + '/segmented/vsfm.0.ply']}
