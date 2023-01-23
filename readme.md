# Run 
1. Open psychopy runner from the folder: ./shortcuts

# create a new subject
1. Edit new_subject.py and run it 

# Procedure for each block
1. Edit session_info.py and **save it**
2. Run main.py 
3. Check if .EDF file got transferred to the result folder 
    ./data/subjectID/sessionID/sessionID_datetime/sessionID_datetime.EDF
4. If exists, can start the next block. If not, transfer manually transfer the edf file from host pc

# transfer edf file from host pc
1. From shortcuts: open psychopy runner
2. Edit transfer_EDF_file.py (EDF_filename should be the same as sessionID)
3. Save and run it
4. If successful, the transfered file should reside in the folder /data/manual_transfer/
5. That file is indeed the data collected in 
6. Move the edf file to the folder for the session 



# changing experiment parameter on the fly
0. There is no safe way to do it. 
1. Backup ./modules/params.py (duplicate and rename)
2. Edit it and save it
3. State that a change is made in session_info.py
4. At the end of block, save the editted params.py to the result folder
5. put original params.py back