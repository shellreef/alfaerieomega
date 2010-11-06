# Created:20050816
# By Jeff Connelly

# vi-edit a directory listing

# Useful vi commands to standardize folder names:

my $a = <<'VI';
" Change foo bar baz => Foo_Bar_Baz
:%s/ \(.\)/_\U\1\E/g
:%s/^\(.\)/\U\1\E/g

" Look for lines without dashes
/^[^-]*$

VI

use strict;
use warnings;

#our ($vi, $outfn) = ("start /b /wait gvim", "vidir.txt");
our ($vi, $outfn) = ("vim", "vidir.txt");

sub vidir
{
    my ($dir) = @_;
    my (@old_fns, @new_fns, %renames);

    opendir(D, $dir) || die "cannot open $dir: $!";
    print "Reading directory...\n";
    @old_fns = grep { -d $_ || !-d $_ } sort readdir(D);
    closedir(D);
    print "In directory: @{[ scalar @old_fns ]} files\n";
    open(OUT,">$outfn") || die "cannot open $outfn: $!";
    for my $file (@old_fns)
    {
        print OUT "$file\n";
    }
    close(OUT);
    print "Loading $vi - make edits to each line (taking care to\n";
    print "not rearrange/delete/add any lines). The files will be renamed.\n";
    print "Waiting...close editor + type exit when done.\n\n";
    system($vi, $outfn);

    open(IN,"<$outfn") || die "cannot open $outfn: $!";
    chomp(@new_fns = <IN>);
    close(IN);
    print "Reloaded @{[ scalar @new_fns ]} filenames.\n";

    if (@new_fns != @old_fns)
    {
        print "The new listing has @{[ scalar @new_fns ]} lines, but the\n";
        print "old listing has @{[ scalar @old_fns ]} lines. Looks like you\n";
        print "deleted or added new lines.\n";
        exit(-1);
    }

    for my $i (0..$#new_fns)
    {
        if ($old_fns[$i] ne $new_fns[$i])
        {
            print "Rename: $old_fns[$i] -> $new_fns[$i]\n";
            $renames{$old_fns[$i]} = $new_fns[$i];
            if (!rename($old_fns[$i], $new_fns[$i]))
            #if (system("git", "mv", $old_fns[$i], $new_fns[$i]) != 0)
            {
                #print "Failed to rename $old_fns[$i] to $new_fns[$i]";
                if (-e $new_fns[$i])
                {
                    if (!-d $new_fns[$i])
                    {
                        die "Failed to rename $old_fns[$i] to $new_fns[$i], exists but isn't a directory to merge";
                    } else {
                        print "Merge: $old_fns[$i] -> $new_fns[$i]\n";
                        #my @cmd = ("cp", "-vr", glob("$old_fns[$i]/*"), "$new_fns[$i]");
                        #print "Command: @cmd\n";
                        #die "failed to merge" if system(@cmd) != 0;
                      
                        $old_fns[$i] =~ s/'/\\'/g;
                        $new_fns[$i] =~ s/'/\\'/g;
                        my $cmd = "cp -vr '$old_fns[$i]/'* '$new_fns[$i]'";
                        print "Command: $cmd\n";
                        die "failed to merge" if system($cmd) != 0;
                        system("rm", "-rf", $old_fns[$i]);
                    }
                }
            }
        }
    }
    print "Done.\n";
}

vidir(".");
