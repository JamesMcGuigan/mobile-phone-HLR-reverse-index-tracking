#!/usr/bin/perl
use strict;
use CGI;
#use JSON;
use Data::Dumper;
use LWP::UserAgent;

my $q = CGI->new();
my $ua = LWP::UserAgent->new();
$ua->agent('RoutoStarAsk/1.0');

my $dest = '447710124669';
my $user = '';
my $pass = '';
my $res = $ua->post( "http://hlr.routotelecom.com/", {
    number => $dest,
    user => $user,
    pass => $pass
});

if ($res->is_error()) {
    # couldn't make request
    print "Couldn't make request: $res->status_line";
} else {
#    my $resp = from_json($res->content());
#    print '<pre>' . Dumper($res) . '</pre>';
    #print $res->['_headers']->['_date'] . "\n" . $res->['_content'] . "\n\n";

    print $res->header("date") . " - " . $res->content;

}
