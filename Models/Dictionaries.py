import sys
import glob
import re
import string

def check_coverage( dictionary, lyrics_path, report_out ):

  """

  Given a dictionary, looks through all .lyrics files 
  found in lyrics_path (recursively) and checks to see 
  if all the words within have pronounciations. Writes
  a report to report_out

  """	

  # Strip (some) punctuation from the lines. Can't use
  # the most efficient built-ins since we want to keep
  # single quotes (frontin' etc) 
  punctuation = ['!', '?', ',']

  # Read dictionary
  dictionary_lines = open( dictionary ).readlines()

  # set up fast check if word is in dict using a set
  dictionary_words = set( [ line.split()[ 0 ] for line in dictionary_lines] )

  # open report file
  report = open( report_out, 'w' )

  # Glob for .lyrics files
  lyric_files = glob.glob( lyrics_path + '*.lyrics')

  # Loop through files
  print ''

  n_lyr = len( lyric_files )
  
  for ilyric, lyric_file in enumerate( lyric_files ):

    # display progress
    print '  checking lyric ' + str( ilyric + 1 ) + ' of ' + str( n_lyr )

    # print to report
    report.write( lyric_file + '\n')
    report.write( '-' * len( lyric_file ) + '\n' )

  	# read lyric file
    lyrics = open( lyric_file ).readlines()
  	
  	# loop through lines
    for line in lyrics[ 1 : ]:

      # skip empty lines and structure lines
      if re.match( '\[.+\]', line.strip() ):

        continue
 
      if line.strip() == '':

        continue

      # Else, strip all unwanted punctuation
      for p in punctuation:

      	line = line.replace( p, '')

      # Finally, loop through words checking if they're in
      # dictionary_words
      for word in line.split():

        # if we can't find it
      	if word.upper() not in dictionary_words:

          # print to report
      	  report.write( word + '\n')

    # a newline here separates files nicely
    report.write( '\n' ) 

  # close report file
  report.close()

  print ''
  return None

if __name__ == '__main__':

  # check number of inputs
  if len( sys.argv[ 1 : ] ) != 3:

  	raise ValueError('You must provide a dictionary, lyrics path and report file')

  # run check_coverage	
  check_coverage( sys.argv[ 1 ], sys.argv[ 2 ],
                 sys.argv[ 3 ] )	
