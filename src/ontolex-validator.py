#!/bin/python
import sys
import getopt
import io
import re
from rdflib import *
from rdflib.namespace import RDF, RDFS, OWL
from xml.sax.saxutils import escape
import logging

logger = logging.getLogger("rdflib.term")
logger.disabled = True

suspicious = 0
minor = 0
major = 0
warnOfMessage = io.StringIO()
endOfMessage = io.StringIO()

outputFormat = "txt"

lexinfo = Namespace("http://www.lexinfo.net/ontology/2.0/lexinfo#")
ontolex = Namespace("http://www.w3.org/ns/lemon/ontolex#")
synsem = Namespace("http://www.w3.org/ns/lemon/synsem#")
decomp = Namespace("http://www.w3.org/ns/lemon/decomp#")
vartrans = Namespace("http://www.w3.org/ns/lemon/vartrans#")
lime = Namespace("http://www.w3.org/ns/lemon/lime#")

lexinfoProps = dict([
    (lexinfo.adjunct,synsem.synArg),
    (lexinfo.possessiveAdjunct,synsem.synArg),
    (lexinfo.predicativeAdjunct,synsem.synArg),
    (lexinfo.comparativeAdjunct,synsem.synArg),
    (lexinfo.superlativeAdjunct,synsem.synArg),
    (lexinfo.prepositionalAdjunct,synsem.synArg),
    (lexinfo.attributiveArg,synsem.synArg),
    (lexinfo.clausalArg,synsem.synArg),
    (lexinfo.declarativeClause,synsem.synArg),
    (lexinfo.gerundClause,synsem.synArg),
    (lexinfo.infinitiveClause,synsem.synArg),
    (lexinfo.interrogativeInfinitiveClause,synsem.synArg),
    (lexinfo.possessiveInfinitiveClause,synsem.synArg),
    (lexinfo.prepositionalGerundClause,synsem.synArg),
    (lexinfo.prepositionalInterrogativeCaluse,synsem.synArg),
    (lexinfo.sententialClause,synsem.synArg),
    (lexinfo.subjunctiveClause,synsem.synArg),
    (lexinfo.complement,synsem.synArg),
    (lexinfo.adverbialComplement,synsem.synArg),
    (lexinfo.objectComplement,synsem.synArg),
    (lexinfo.predicativeAdjective,synsem.synArg),
    (lexinfo.predicativeAdverb,synsem.synArg),
    (lexinfo.predicativeNominative,synsem.synArg),
    (lexinfo.copulativeArg,synsem.synArg),
    (lexinfo.copulativeSubject,synsem.synArg),
    (lexinfo.object,synsem.synArg),
    (lexinfo.adpositionalObject,synsem.synArg),
    (lexinfo.prepositionalObject,synsem.synArg),
    (lexinfo.postpositionalObject,synsem.synArg),
    (lexinfo.directObject,synsem.synArg),
    (lexinfo.genitiveObject,synsem.synArg),
    (lexinfo.indirectObject,synsem.synArg),
    (lexinfo.postPositiveArg,synsem.synArg),
    (lexinfo.subject,synsem.synArg),
    (lexinfo.copulativeSubject,synsem.synArg)
])

lemonPropDomains = dict([
(ontolex.lexicalizedSense,ontolex.LexicalConcept),
(ontolex.reference,(ontolex.LexicalSense,synsem.OntoMap)),
(ontolex.isConceptOf,ontolex.LexicalConcept),
(ontolex.isSenseOf,ontolex.LexicalSense),
(ontolex.canonicalForm,ontolex.LexicalEntry),
(ontolex.usage,ontolex.LexicalSense),
(ontolex.sense,ontolex.LexicalEntry),
(ontolex.writtenRep,ontolex.Form),
(ontolex.otherForm,ontolex.LexicalEntry),
(ontolex.denotes,ontolex.LexicalEntry),
(ontolex.phoneticRep,ontolex.Form),
(ontolex.evokes,ontolex.LexicalEntry),
(ontolex.lexicalForm,ontolex.LexicalEntry),
(ontolex.representation,ontolex.Form),
(ontolex.isEvokedBy,ontolex.LexicalConcept),
(ontolex.morphologicalPattern,ontolex.LexicalEntry),
(ontolex.isLexicalizedSenseOf,ontolex.LexicalConcept),
(synsem.submap,synsem.OntoMap),
(synsem.marker,synsem.SyntacticArgument),
(synsem.ontoCorrespondence,(synsem.OntoMap,ontolex.LexicalSense)),
(synsem.synBehavior,ontolex.LexicalEntry),
(synsem.synArg,synsem.SyntacticFrame),
(synsem.ontoMapping,synsem.OntoMap),
(synsem.optional,synsem.SyntacticArgument),
(synsem.condition,synsem.OntoMap),
(decomp.constituent,(ontolex.LexicalEntry,decomp.Component)),
(decomp.correspondsTo,decomp.Component),
(decomp.subterm,ontolex.LexicalEntry),
(vartrans.translatableAs,ontolex.LexicalEntry),
(vartrans.category,vartrans.LexicoSemanticRelation),
(vartrans.conceptRel,ontolex.LexicalConcept),
(vartrans.lexicalRel,ontolex.LexicalEntry),
(vartrans.senseRel,ontolex.LexicalSense),
(vartrans.trans,vartrans.TranslationSet),
(vartrans.relates,vartrans.LexicoSemanticRelation),
(lime.avgSynonymy,lime.ConceptualizationSet),
(lime.conceptualDataset,(lime.LexicalLinkset,lime.ConceptualizationSet)),
(lime.lexicalEntries,(lime.Lexicon,lime.LexicalizationSet,lime.ConceptualizationSet)),
(lime.percentage,(lime.LexicalizationSet,lime.LexicalLinkset)),
(lime.lexicalizationModel,lime.LexicalizationSet),
(lime.resourceType,(lime.LexicalizationSet,lime.LexicalLinkset)),
(lime.lexicalizations,lime.LexicalizationSet),
(lime.referenceDataset,(lime.LexicalizationSet,lime.LexicalLinkset)),
(lime.avgAmbiguity,lime.ConceptualizationSet),
(lime.entry,lime.Lexicon),
(lime.avgNumOfLinks,lime.LexicalLinkset),
(lime.avgNumOfLexicalizations,lime.LexicalizationSet),
(lime.lexiconDataset,(lime.LexicalizationSet,lime.ConceptualizationSet)),
(lime.partition,(lime.LexicalizationSet,lime.LexicalLinkset)),
(lime.references,(lime.LexicalizationSet,lime.LexicalLinkset)),
(lime.concepts,(ontolex.ConceptSet,lime.LexicalLinkset,lime.ConceptualizationSet)),
(lime.linguisticCatalog,lime.Lexicon),
(lime.links,lime.LexicalLinkset),
(lime.conceptualizations,lime.ConceptualizationSet),
(lime.language,(ontolex.LexicalEntry,lime.Lexicon,lime.ConceptSet,lime.LexicalizationSet))
])

lemonPropRanges = dict([
(ontolex.isDenotedBy,ontolex.LexicalEntry),
(ontolex.canonicalForm,ontolex.Form),
(ontolex.isReferenceOf,(ontolex.LexicalSense,synsem.OntoMap)),
(ontolex.lexicalForm,ontolex.Form),
(ontolex.isSenseOf,ontolex.LexicalEntry),
(ontolex.lexicalizedSense,ontolex.LexicalSense),
(ontolex.evokes,ontolex.LexicalConcept),
(ontolex.isLexicalizedSenseOf,ontolex.LexicalSense),
(ontolex.isEvokedBy,ontolex.LexicalEntry),
(ontolex.sense,ontolex.LexicalSense),
(ontolex.concept,ontolex.LexicalConcept),
(ontolex.otherForm,ontolex.Form),
(synsem.ontoCorrespondence,synsem.SyntacticArgument),
(synsem.ontoMapping,ontolex.LexicalSense),
(synsem.synBehavior,synsem.SyntacticFrame),
(synsem.submap,synsem.OntoMap),
(synsem.synArg,synsem.SyntacticArgument),
(decomp.subterm,ontolex.LexicalEntry),
(decomp.constituent,decomp.Component),
(decomp.correspondsTo,(ontolex.LexicalEntry,synsem.SyntacticArgument)),
(vartrans.relates,(ontolex.LexicalEntry,ontolex.LexicalSense,ontolex.LexicalConcept)),
(vartrans.conceptRel,ontolex.LexicalConcept),
(vartrans.trans,vartrans.Translation),
(vartrans.lexicalRel,ontolex.LexicalEntry),
(vartrans.senseRel,ontolex.LexicalSense),
(vartrans.translatableAs,ontolex.LexicalEntry),
(lime.partition,(lime.LexicalizationSet,lime.LexicalLinkset)),
(lime.conceptualDataset,ontolex.ConceptSet),
(lime.linguisticCatalog,"http://purl.org/vocommons/voaf#Vocabulary"),
(lime.entry,ontolex.LexicalEntry),
(lime.lexiconDataset,lime.Lexicon),
(lime.resourceType,RDFS.Class)
])

lemonDataProperties = set([
ontolex.writtenRep,
ontolex.phoneticRep,
ontolex.representation,
synsem.optional,
lime.avgSynonymy,
lime.avgNumOfLexicalizations,
lime.links,
lime.language,
lime.referenceDataset,
lime.concepts,
lime.lexicalizations,
lime.avgNumOfLinks,
lime.lexicalEntries,
lime.conceptualizations,
lime.percentage,
lime.avgAmbiguity,
lime.references,
])

lemonURIs = set([
decomp.Component,
decomp.constituent,
decomp.correspondsTo,
decomp.subterm,
lime.avgAmbiguity,
lime.avgNumOfLexicalizations,
lime.avgNumOfLinks,
lime.avgSynonymy,
lime.concepts,
lime.conceptualDataset,
lime.conceptualizations,
lime.ConceptualizationSet,
lime.entry,
lime.language,
lime.lexicalEntries,
lime.lexicalizationModel,
lime.lexicalizations,
lime.LexicalizationSet,
lime.LexicalLinkset,
lime.Lexicon,
lime.lexiconDataset,
lime.linguisticCatalog,
lime.links,
lime.partition,
lime.percentage,
lime.referenceDataset,
lime.references,
lime.resourceType,
ontolex.Affix,
ontolex.canonicalForm,
ontolex.concept,
ontolex.ConceptSet,
ontolex.denotes,
ontolex.evokes,
ontolex.Form,
ontolex.isConceptOf,
ontolex.isDenotedBy,
ontolex.isEvokedBy,
ontolex.isLexicalizedSenseOf,
ontolex.isReferenceOf,
ontolex.isSenseOf,
ontolex.LexicalConcept,
ontolex.LexicalEntry,
ontolex.lexicalForm,
ontolex.lexicalizedSense,
ontolex.LexicalSense,
ontolex.morphologicalPattern,
ontolex.MultiwordExpression,
ontolex.otherForm,
ontolex.phoneticRep,
ontolex.reference,
ontolex.representation,
ontolex.sense,
ontolex.usage,
ontolex.Word,
ontolex.writtenRep,
synsem.condition,
synsem.isA,
synsem.marker,
synsem.objOfProp,
synsem.ontoCorrespondence,
synsem.OntoMap,
synsem.OntoMap,
synsem.ontoMapping,
synsem.optional,
synsem.propertyDomain,
synsem.propertyRange,
synsem.subjOfProp,
synsem.submap,
synsem.synArg,
synsem.synBehavior,
synsem.SyntacticArgument,
synsem.SyntacticArgument,
synsem.SyntacticFrame,
vartrans.category,
vartrans.conceptRel,
vartrans.ConceptualRelation,
vartrans.lexicalRel,
vartrans.LexicalRelation,
vartrans.LexicoSemanticRelation,
vartrans.relates,
vartrans.senseRel,
vartrans.SenseRelation,
vartrans.source,
vartrans.target,
vartrans.TerminologicalRelation,
vartrans.trans,
vartrans.translatableAs,
vartrans.translation,
vartrans.Translation,
vartrans.TranslationSet,
])

def leniter(iterator):
    """leniter(iterator): return the length of an iterator, consuming it."""
    if hasattr(iterator, "__len__"):
        return len(iterator)
    nelements = 0
    for _ in iterator:
        nelements += 1
    return nelements

def computeTypes(g,elem):
    ct = set()
    for pred, obj in g.predicate_objects(elem):
        if pred in lemonPropDomains.keys():
            ct.add(lemonPropDomains[pred])
        elif pred in lexinfoProps.keys():
            ct.add(lemonPropDomains[lexinfoProps[pred]])
        elif pred in lemonDataProperties and not isinstance(obj,Literal):
            err("DP_INVALID_OBJ","URI as object of " + pred)
        elif is_lemon_uri(pred) and pred not in lemonDataProperties and isinstance(obj,Literal):
            err("OP_INVALID_OBJ","Literal as object of " + pred)
    for subj, pred in g.subject_predicates(elem):
        if pred in lemonPropRanges:
            ct.add(lemonPropRanges[pred])
        elif pred in lexinfoProps.keys():
            ct.add(lemonPropRanges[lexinfoProps[pred]])
    return harmonizeType(ct)

def harmonizeType(ct):
    if len(ct) <= 1:
        return ct
    ct_new = set()
    for c in ct:
        if type(c) == tuple:
            o = [c2 for c2 in c if c2 in ct]
            if not o:
                ct_new.add(c)
        else:
            ct_new.add(c)
    return ct_new


def validateLemonElement(g,types,elem):

    if elem in types.keys():
        computedTypes = set(types[elem]) | computeTypes(g,elem)
    else:
        computedTypes = computeTypes(g,elem)
    if len(computedTypes) > 1:
        warn("MULT_TYPES",elem + " has multiple types: " + str([str(t)[35:] for t in computedTypes]))
    for type in computedTypes:
        if type == ontolex.LexicalEntry:
            validateLexicalEntry(g,types,elem)
        if type == ontolex.LexicalSense:
            validateLexicalSense(g,types,elem)
        if type == ontolex.Form:
            validateForm(g,types,elem)
        if type == synsem.Component:
            validateComponent(g,types,elem)
        if type == lime.Lexicon:
            validateLexicon(g,types,elem)

def validateLexicalEntry(g,types,elem):
    ncanonicalForms = leniter(g.objects(elem,ontolex.canonicalForm)) 
    if ncanonicalForms == 0:
        warn("ENTRY_NO_CAN_FORM","Lexical Entry " + elem + " does not have a canonical form")
    elif ncanonicalForms > 1:
        err("ENTRY_MANY_CAN_FORMS","Lexical Entry " + elem + " has multiple canonical forms")
    nlanguages = leniter(g.objects(elem,lime.language))
    if nlanguages == 0:
        note("ENTRY_NO_LANG","Lexical Entry " + elem + " does not have a language")
    elif nlanguages > 1:
        err("ENTRY_MANY_LANG","Lexical Entry " + elem + " has multiple languages")
    nlabels = leniter(g.objects(elem,RDFS.label))
    if nlabels == 0:
        note("ENTRY_NO_RDFS_LABEL","Lexical Entry " + elem + " does not have a RDFS label")

def validateLexicalSense(g,types,elem):
    nreferences = leniter(g.objects(elem,ontolex.reference))
    nsubsense = 0#leniter(g.objects(elem,lemon.subsense))
    if nreferences == 0 and nsubsense == 0:
        err("SENSE_NO_REF","Lexical Sense " + elem + " does not have a reference")
    elif nreferences > 1:
        warn("SENSE_MANY_REF","Lexical Sense " + elem + " has multiple references")

def validateForm(g,types,elem):
    nwrittenrep = leniter(g.objects(elem,ontolex.writtenRep))
    if nwrittenrep == 0:
        err("FORM_NO_REP","Form " + elem + " does not have a written representation")

def validateComponent(g,types,elem):
    ncomponents = leniter(g.objects(elem,ontolex.correspondsTo))
    if ncomponents == 0:
        warn("COMPONENT_NO_ELEM","Component " + elem + " does not have an element")
    if ncomponents > 1:
        err("COMPONENT_MANY_ELEM","Component " + elem + " has more than one element")

def validateLexicon(g,types,elem):
    nentries = leniter(g.objects(elem,lime.entry))
    nlanguages = leniter(g.objects(elem,lime.language))
    if nentries == 0:
        err("LEXICON_EMPTY","Lexicon " + elem + " contains no values")
    if nlanguages == 0:
        err("LEXICON_NO_LANG","Lexicon " + elem + " does not have a language")
    elif nlanguages > 1:
        err("LEXICON_MANY_LANG","Lexicon " + elem + " has multiple languages")


def validateBoolLiteral(lit):
    if lit.datatype != XSD.boolean:
        warn("BOOL_NO_TYPE","Boolean value not marked as xsd:boolean")
    if lit.lower() != "true" and lit.lower() != "false" and lit != "1" and lit != "0":
        err("BOOL_BAD_VALUE","Invalid boolean value: " + lit)

languageRegex = "^(...?)(-[A-Za-z]{4})?(-[A-Za-z]{2}|-[0-9]{3})?((-[A-Za-z0-9]{5,8}|-[0-9][A-Za-z0-9]{3})*)((-[A-WY-Za-wy-z0-9]-\\w{2,8})*)(-[Xx]-\\w{1,8})?$"

def validateLanguage(l):
    if not re.match(languageRegex,l):
        err("BAD_LANG","Invalid language code: " + l)

def validateRule(rule):
    if rule.count("~") != 1 or rule.count("/") > 1:
        err("BAD_RULE","Invalid rule: " + rule)

def validateText(lit):
    if lit.language is None:
        err("NO_LANG","Language tag missing from literal " + lit)
    else:
        validateLanguage(lit.language)


def note(code,msg):
    global suspicious
    global endOfMessage
    if outputFormat == "txt":
        endOfMessage.write("[NOTE ] " + msg + "\n")
    elif outputFormat == "xml":
        endOfMessage.write( "<note code=\""+code+"\">" + escape(msg) + "</note>" +"\n")
    elif outputFormat == "html":
        endOfMessage.write( "<div class=\"lemon-validator-note\">" + escape(msg) + " <a href=\"errors.html#" + code.lower() + "\">["+code+"]</a></div>" +"\n")
    suspicious = suspicious + 1

def warn(code,msg):
    global minor
    global warnOfMessage
    if outputFormat == "txt":
        warnOfMessage.write( "[WARN ] " + msg+"\n")
    elif outputFormat == "xml":
        warnOfMessage.write( "<warn code=\""+code+"\">" + escape(msg) + "</warn>"+"\n")
    elif outputFormat == "html":
        warnOfMessage.write( "<div class=\"lemon-validator-warn\">" + escape(msg) + " <a href=\"errors.html#" + code.lower() + "\">["+code+"]</a></div>"+"\n")
    minor = minor + 1

def err(code,msg):
    global major
    if outputFormat == "txt":
        print("[ERROR] " + msg)
    elif outputFormat == "xml":
        print("<error code=\""+code+"\">" + escape(msg) + "</error>")
    elif outputFormat == "html":
        print("<div class=\"lemon-validator-error\">" + escape(msg) + " <a href=\"errors.html#" + code.lower() + "\">["+code+"]</a></div>")
    major = major + 1

def is_lemon_uri(uri):
    return (uri.startswith(ontolex) or uri.startswith(synsem) or 
            uri.startswith(decomp) or uri.startswith(vartrans) or
            uri.startswith(lime))

def main(argv):
    global outputFormat
    global endOfMessage
    global warnOfMessage
    optlist, args = getopt.getopt(argv[1:],"f:o:")
    optdict = dict(optlist)
    if len(args) != 1:
        print("Usage:\n\t./lemon-validator.py [-f xml|turtle] [-o txt|xml|html] file:/lemon-file.rdf")
        exit()

    g = Graph()

    if "-o" in optdict.keys():
        outputFormat = optdict["-o"]
        if outputFormat != "txt" and outputFormat != "xml" and outputFormat != "html":
            print("Invalid argument -o " + outputFormat)
            exit()
        if outputFormat == "xml":
            print("<report>")

    try:
        if "-f" in optdict.keys():
            g.parse(args[0],format=optdict["-f"])
        else:
            g.parse(args[0])
    except Exception as e: 
        err("INVALID_RDF","Failed to parse as RDF: " + str(e))
        exit()

    types = {}

    for subj, pred, obj in g:
        if pred == RDF.type:
            if subj in types.keys():
                types[subj].append(obj)
            else:
                types[subj] = [obj]
        elif pred == RDFS.subPropertyOf:
            if subj in types.keys():
                types[subj].add(obj)
            else:
                types[subj] = set([obj])
        if is_lemon_uri(subj) and subj not in lemonURIs:
            err("NOT_LEMON_URI","Not a lemon URI : " + subj)
        elif is_lemon_uri(obj) and obj not in lemonURIs:
            err("NOT_LEMON_URI","Not a lemon URI: " + obj)
        elif is_lemon_uri(pred) and pred not in lemonURIs:
            err("NOT_LEMON_URI","Not a lemon URI: " + pred)
        if isinstance(subj,BNode) and pred != RDF.first and pred != RDF.rest:
            warn("BNODE","Blank node usage: _:bnode " + pred + " " + obj)
        #if isinstance(subj, URIRef) and  subj.startswith(lemonOld):
        #    warn("OLD_LEMON_URI","Please update lemon namespace to http://lemon-model.net/lemon#")


    checked = {}

    for subj, pred, obj in g:
        if pred in lemonDataProperties and isinstance(obj,Literal):
            if pred == synsem.optional:
                validateBoolLiteral(obj)
            elif pred == lime.language:
                if obj.language is not None:
                    err("LANG_ON_LANG","Language tag on language identifier")
                validateLanguage(obj)
            else:
                validateText(obj)
        if is_lemon_uri(pred):
            if subj not in checked:
                validateLemonElement(g,types,subj)
                checked[subj] = True
        elif pred.startswith(RDF.uri) or pred.startswith(RDFS.uri) or pred.startswith(OWL) or pred.startswith(lexinfo):
            True
        elif pred in types.keys() and OWL.AnnotationProperty in types[pred]:
            True
        else:
            note("UNRECOGNIZED","Unrecognized triple: " + str(subj) + " " + str(pred) + " " + str(obj))
        
    print(warnOfMessage.getvalue())
    print(endOfMessage.getvalue())

    if outputFormat == "txt":
        print("There were " + str(suspicious) + " advisories, " + str(minor) + " warnings and " + str(major) + " errors")
    elif outputFormat == "xml":
        print("</report>")
    elif outputFormat == "html" and suspicious == 0 and minor == 0 and major == 0:
        print("<div>No errors</div>")

if __name__=='__main__': main(sys.argv)
