# Build the acronym list declared in glosario.tex.
add_cus_dep('nlo', 'nls', 0, 'make_nomenclature');

sub make_nomenclature {
    my ($base) = @_;
    return system('makeindex', '-s', 'nomencl.ist',
                  '-o', "$base.nls", '-t', "$base.nlg", "$base.nlo");
}
