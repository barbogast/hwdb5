class WrongTreeError(Exception): pass
class MixedBracketsError(Exception): pass


def keys_have_brackets(d):
    with_brackets = 0
    without_brackets = 0

    for k in d.keys():
        if k.startswith('<'):
            if not k.endswith('>'):
                raise AssertionError(d)
            with_brackets += 1
        else:
            without_brackets += 1
    if with_brackets and without_brackets:
        raise MixedBracketsError('Dict contains keys with _and_ without brackets: %s'%d)
    return bool(with_brackets)


def inflate_tree(tree, csv_files=None, csv_label=None):
    """ For examples see unit tests """
    def _inflate_list(l):
        if not isinstance(l, (list, tuple)):
            raise Exception('Element %r is a %s but should be list/tuple'% (l, type(l)))

        inflated_elements = []
        for el in l:
            if isinstance(el, basestring):
                inflated_elements.append({'<name>': el})

            elif isinstance(el, dict):
                if keys_have_brackets(el):
                    raise WrongTreeError('The keys in this dict should not have brackets: %s; keys: %s'%(el, el.keys()))
                for k, v in el.iteritems():
                    inflated_el = { '<name>': k }

                    if isinstance(v, dict):
                        inflated_el.update(v)
                        if not keys_have_brackets(inflated_el):
                            raise WrongTreeError('The keys in this dict must have brackets: %s; keys: %s'%(el, el.keys()))
                        if '<children>' in inflated_el:
                            if not isinstance(inflated_el['<children>'], (tuple, list)):
                                raise WrongTreeError('Expected list, got type %s: %s'%(type(inflated_el['<children>']), inflated_el['<children>']))
                            inflated_el['<children>'] = _inflate_list(inflated_el['<children>'])
                        if '<no_connector>' in inflated_el:
                            if not isinstance(inflated_el['<no_connector>'], (tuple, list)):
                                raise WrongTreeError('Expected list, got type %s: %s'%(type(inflated_el['<no_connector>']), inflated_el['<no_connector>']))
                            inflated_el['<no_connector>'] = _inflate_list(inflated_el['<no_connector>'])
                        if '<connectors>' in inflated_el:
                            if not isinstance(inflated_el['<connectors>'], (tuple, list)):
                                raise WrongTreeError('Expected list, got type %s: %s'%(type(inflated_el['<connectors>']), inflated_el['<connectors>']))
                            inflated_el['<connectors>'] = _inflate_list(inflated_el['<connectors>'])
                        if '<import>' in inflated_el:
                            name = inflated_el.pop('<import>')
                            if csv_label in csv_files[name]:
                                inflated_el.setdefault('<children>', []).extend(csv_files[name][csv_label])

                    elif isinstance(v, list):
                        inflated_el['<children>'] = _inflate_list(v)

                    else:
                        raise WrongTreeError('%s %s' % (type(v), v))

                    inflated_elements.append(inflated_el)

            else:
                raise WrongTreeError(el)

        return inflated_elements

    return _inflate_list(tree)
