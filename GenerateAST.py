import sys
from tree_sitter import Language, Parser
import networkx as nx
import os
from networkx.drawing.nx_pydot import write_dot
import matplotlib.pyplot as plt
import glob
import sys
sys.path.append('/home/vcp/haorend/function_sum_api/api/')
from function_sum_api import code_sum
sys.setrecursionlimit(10000) #例如这里设置为十万
gar=['()','[]']
gar_w=[',','\"','(',')','{','}','\'',':','+','=','-','.','argument_list','string','def','identifier','call']


shapex={
    'import_statement':"box",
    'import_from_statement':"box",
    'comment':"box",
    'function_definition':'box',
    'return_statement':'box',
    'block':'box',
    'if_statement':'box',
    'decorated_definition':'box',
    'class_definition':'box',
    'block':'point',
    'expression_statement':'box',
    'identifier':'point'

}

colorx={
    'import_statement':"#f48b29",
    'import_from_statement':'#f48b29',
    'function_definition':'#cee6b4',
    'comment':"#f0c929",
    'return_statement':"#f0c929",
    'block':'white',
    'if_statement':'#9ecca4',
    'decorated_definition':'#c8c6a7',
    'class_definition':'#ffdf91',
    'block':'#121013',
    'expression_statement':'#121013',
    'identifier':'#121013',
}
#'expression_statement',

return_out=['import_from_statement',
            'import_statement','return_statement',
            'boolean_operator','for_statement',
            'while_statement','with_clause','decorator','if_statement',
            ]
# return_out=[]
# jump_out=[]
jump_out=['while','def','assert','.',':','highlight','with',
            'is','(',')',',','integer','=','==','string','none','true',
            'false','in','class','not','[',']',"\"",'expression_statement',]

def read_file(filepath):
    fp=open(filepath)
    content=fp.readlines()
    fp.close()
    tmp=''
    for i in content:
        tmp = tmp + i
    return tmp



class ast_node(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

def match_from_span(node, blob):
    lines = blob.decode().split('\n')
    line_start = node.start_point[0]
    line_end = node.end_point[0]
    char_start = node.start_point[1]
    char_end = node.end_point[1]
    if line_start != line_end:
        return '\n'.join([lines[line_start][char_start:]] + lines[line_start+1:line_end] + [lines[line_end][:char_end]])
    else:
        return str(lines[line_start][char_start:char_end])

def generate_pos_id(node,encode):
    line_start = node.start_point[0]
    line_end = node.end_point[0]
    char_start = node.start_point[1]
    char_end = node.end_point[1]
    
    id = "line_star:"+str(line_start)+','+"line_end:"+str(line_end)+'|'+"char_star:"+str(char_start)+','+"char_end:"+str(char_end)
    return id



def Write_node(file_in,atr,type_atr):
    global shapex,colorx
    if type_atr in list(shapex.keys()):
        type_in="\""+atr.replace('\n','\\n').replace('\"','\'')+"\""+"["+"shape="+"\""+shapex[type_atr] +"\""+','+"fillcolor="+"\""+ colorx[type_atr] +"\""+','+"style="+"filled"+"]"+";\n"
    else:
        type_in="\""+atr.replace('\n','\\n').replace('\"','\'')+"\""+"["+"shape="+"\""+"box"+"\""+','+"fillcolor="+"\"" + "white"+"\""+','+"style="+"filled"+"]"+";\n"
    file_in.writelines(type_in)

def Write_edge(file_in,atr_in,atr_out,type_atr):
    global shapex,colorx
    if type_atr in list(shapex.keys()):
        atr="\""+str(atr_in).replace('\n','\\n').replace('\"','\'')+"\""+'->'+"\""+str(atr_out).replace('\n','\\n').replace('\"','\'')+"\""+";\n"
    else:
        atr="\""+str(atr_in).replace('\n','\\n').replace('\"','\'')+"\""+'->'+"\""+str(atr_out).replace('\n','\\n').replace('\"','\'')+"\""+";\n"
    file_in.writelines(atr)
    


def traverse(node, Graph, encoded_code,file_in):
    if node.child_count == 0:
        return
    if node.type == 'import_statement' or node.type == 'import_from_statement':
        global import_lists
        import_lists.append(match_from_span(node, encoded_code))
    if node.type in return_out:
        return


    # if node.type == "function_definition":
    #     f = open('result_dot/test1.txt','a')
    #     f.write(match_from_span(node, encoded_code))
    #     f.write('\n')
    #     f.write('**************************************************************************\n')
    #     f.close()

    if node.type == "function_definition":
        global function_list
        function_list.append(match_from_span(node, encoded_code))


    if node.type == 'module':
        Graph.add_node("MODULE",type="\""+node.type+"\"", color="lightblue")
        Write_node(file_in,"MODULE",node.type)
        
        for n in node.children:
            if n.type not in jump_out:
                child =match_from_span(n, encoded_code)+","+"type="+ "\'" + n.type + "\'" +"\\n"+ generate_pos_id(n,encoded_code) 
                Graph.add_node(child)
                Write_node(file_in,child,n.type)
                Graph.add_edge("MODULE",child,color="lightblue")
                Write_edge(file_in,"MODULE",child,"lightblue")
                traverse(n,Graph,encoded_code,file_in)
    elif node.type == 'block':
         for n in node.children:
            if n.type not in jump_out:
                tmp=match_from_span(node, encoded_code)
                if len(tmp)>=20:
                    tmp=tmp[:20]

                child = match_from_span(n, encoded_code)+","+"type="+ "\'" + n.type + "\'"+"\\n" + generate_pos_id(n,encoded_code)
                father = "type="+ "\'" + "INFORMATION BLOCK" + "\'"+"\\n" + generate_pos_id(node,encoded_code) 
                Graph.add_node(child)
                Write_node(file_in,child,n.type)
                Graph.add_edge(father,child)
                Write_edge(file_in,father,child,"lightblue")
                traverse(n,Graph,encoded_code,file_in)

    else:
        for n in node.children:
            if n.type not in jump_out:
                tmp=match_from_span(n, encoded_code)
                if tmp in gar:
                    continue
                elif n.type == 'block':
                    tmp=match_from_span(n, encoded_code)
                    if len(tmp)>=20:
                        tmp=tmp[:20]
                    child = "type="+ "\'" + "INFORMATION BLOCK" + "\'"+"\\n" + generate_pos_id(n,encoded_code)
                    father = match_from_span(node, encoded_code)+","+"type="+ "\'" + node.type + "\'"+"\\n" + generate_pos_id(node,encoded_code) 
                    Graph.add_node(child)
                    Write_node(file_in,child,n.type)
                    Graph.add_edge(father,child)
                    Write_edge(file_in,father,child,"lightblue")
                    traverse(n,Graph,encoded_code,file_in)
                else:
                    
                    child = match_from_span(n, encoded_code)+","+"type="+ "\'" + n.type + "\'"+"\\n" + generate_pos_id(n,encoded_code)
                    father = match_from_span(node, encoded_code)+","+"type="+ "\'" + node.type + "\'"+"\\n" + generate_pos_id(node,encoded_code) 
                    Graph.add_node(child)
                    Write_node(file_in,child,n.type)
                    Graph.add_edge(father,child)
                    Write_edge(file_in,father,child,"lightblue")
                    traverse(n,Graph,encoded_code,file_in)




def write_together(f,getin):
    tmp=''
    for i in getin:
        tmp=tmp+i+'\n'
    tmp=tmp[:-2].replace('\n','\\n').replace('\"','\'')
    atr="\"MODULE\""+'->'+"\""+tmp+"\""+"\n" 
    node="\""+tmp+"\""+"[shape=\"box\",fillcolor=\"#f48b29\",style=filled]"+";\n"
    f.write(node)
    f.write(atr)

    


def file_parse(path,name):
    Language.build_library('../build/my-languages.so', ['../tree-sitter-python'])
    PY_LANGUAGE = Language('../build/my-languages.so', 'python')
    parser = Parser()
    parser.set_language(PY_LANGUAGE)
    code = read_file(str(path))
    encoded_code = bytes(code, "utf8")
    tree = parser.parse(encoded_code)
    cursor = tree.walk()
    root_node = tree.root_node

    Graph = nx.DiGraph()
    f= open('result_dot/'+str(name)+'.dot','w') 
    f.write('digraph G{\n')
    f.write('rankdir="LR";\n')
    traverse(root_node,Graph,encoded_code,f)
    global import_lists
    write_together(f,import_lists)


    f.write("}")
    f.close()

    
    #write_in_dot(Graph)
    return None


def write_in_dot(G):
    
    with open('ast.dot','w') as f:
    
        f.write('digraph G{\n')
        for node in G.nodes:
            # atr='[type='+"\""+node.type+"\""+']'+";"+'\n'
            # f.writeline(node,atr)
            atr="\""+str(node).replace('\n','\\n').replace('\"','\'')+"\""+";\n"
            f.write(atr)
        for edge in G.edges:
            atr="\""+str(edge[0]).replace('\n','\\n').replace('\"','\'')+"\""+'->'+"\""+str(edge[1]).replace('\n','\\n').replace('\"','\'')+"\""+";\n"
            f.write(atr)
        f.write("}")


def remove_duplicate(name):
    name_in ='result_dot/'+str(name)+'.dot'
    name_out='result_dot/'+'new_'+str(name)+'.dot'
    f=open(name_in,"r")
    outfile=open(name_out,'w')
    lines_seen = set()  
    for line in f:
        line =  line.strip('\n')
        if line not in lines_seen:
            outfile.write(line+'\n')
            lines_seen.add(line)
    f.close()
    outfile.close()
    os.remove(name_in)
    
def write_txt(filename,result):
    f = open(filename,'w')
    global function_list
    for i in range(len(function_list)):
        f.write(function_list[i])
        f.write('\n\n\n\n')
        f.write(result[i])
        f.write('\n\n\n\n')
    f.close()


def run_model():
    global function_list
    code=function_list
    print('running model')
    load_model_path = 'brandnewtxt/code-to-text/pytorch_model.bin'
    result = code_sum(code,load_model_path)
    return result


def generate_txt(file_path):
    name =  file_path.split('/')[-1].split('.')[-2]
    tmp_name = 'result_dot/'+name+'.txt'
    f = open(tmp_name,'w')
    f.truncate();
    f.close
    global function_list
    function_list=[]
    global import_lists
    import_lists=[]
    print('processing file with modal',name)
    name=file_path.split('/')[-1].split('.')[0]
    file_parse(file_path,name)
    print('parsing')
    remove_duplicate(name)
    result = run_model()
    write_txt(tmp_name,result)

def generate_markdown(f,f_short,file_path):
    name =  file_path.split('/')[-1].split('.')[-2]
    title='# '+str(name)+ '.py'+ '\n'
    f.write(title)
    f_short.write(title)
    tmp_path = 'path : ' + file_path + '\n'
    f.write(tmp_path)
    f_short.write(tmp_path)
    global function_list
    function_list=[]
    global import_lists
    import_lists=[]
    print('processing file with modal',name)
    name=file_path.split('/')[-1].split('.')[0]
    file_parse(file_path,name)
    print('parsing')
    remove_duplicate(name)
    result = run_model()
    code_here='```python\n'
    code_here_2='\n```\n'
    for i in range(len(function_list)):
        tmp_title ='## '+ function_list[i].split('\n')[0].split('(')[0][4:] + '\n'
        f.write(tmp_title)
        f.write('\n')
        
        tmp_result = '**' +result[i]+ '**'
        f.write(tmp_result)
        f.write('\n\n\n\n')
        f.write(code_here)
        f.write(function_list[i])
        f.write(code_here_2)
        f.write('\n\n\n\n')

        title_short = function_list[i].split('\n')[0].split('(')[0][4:]+' : '+ tmp_result +'\n'
        f_short.write(title_short)
        f_short.write('\n\n\n\n')



def judge_py(path):
    if path.split('.')[-1] == 'py':
        return True
    else:
        return False




if __name__ == '__main__':
#     #path = '/home/vcp/tianyih/repo/WebFramework/flask/tests/'
    
    path='/home/vcp/wenlan/wenlan/file_level_sum/call_graph/YOLOv5master'
    name=path.split('/')[-1]
    sys_cmd='python pysa/ '+path+' --multi'
    
    os.system(sys_cmd)


    markdown_name= 'markdown_files/'+name+'_Markdown.md'
    markdown_short_name = 'markdown_files/'+name+'_Markdown_short.md'


    f = open(markdown_name,"w")
    f2 = open(markdown_short_name,'w')
    # for line in open('path_result.txt'):
    #     generate_txt(str(line[:-1]))

    
    filename = 'path_txt/' + name +'.txt'


    for line in open(filename):
        if judge_py(str(line[:-1])):
            generate_markdown(f,f2,str(line[:-1]))

    f.close()
    f2.close()

    # f= open('path_result.txt','w')
    # f.truncate()
    # f.close()


    # for filename in glob.glob('/home/vcp/tianyih/repo/WebFramework/flask/tests/*.py'):
    #     name =  filename.split('/')[-1].split('.')[-2]
    #     tmp_name = 'result_dot/'+name+'.txt'
    #     f = open(tmp_name,'w')
    #     f.truncate();
    #     f.close
    #     global function_list
    #     function_list=[]
    #     global import_lists
    #     import_lists=[]
    #     print(filename)
    #     name=filename.split('/')[-1].split('.')[0]
    #     file_parse(filename,name)
    #     remove_duplicate(name)
    #     result = run_model()
    #     write_txt(tmp_name,result)

    # for filename in glob.glob('/home/vcp/tianyih/repo/WebFramework/flask/tests/*.py'):
    #     global import_lists
    #     import_lists=[]
    #     print(filename)
    #     name=filename.split('/')[-1].split('.')[0]
    #     file_parse(filename,name)
    #     remove_duplicate(name)
