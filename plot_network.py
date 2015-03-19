#!/usr/bin/env python

#    This program is part of the UCLA Multimodal Connectivity Package (UMCP)
#
#    UMCP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Copyright 2013 Jesse Brown

import numpy as np
import scipy.stats
from mayavi import mlab
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import colorConverter

import core
colors = {'c': (0.0, 0.75, 0.75), 'b': (0.0, 0.0, 1.0), 'w': (1.0, 1.0, 1.0), 'g': (0.0, 0.5, 0.0), 'y': (0.75, 0.75, 0), 'k': (0.0, 0.0, 0.0), 'r': (1.0, 0.0, 0.0), 'm': (0.75, 0, 0.75)}

def plot_matrix(connectmat_file, centers_file, threshold_pct=5, weight_edges=False,
                node_scale_factor=2, edge_radius=.5, resolution=8, name_scale_factor=1,
                names_file=None, node_indiv_colors=[], highlight_nodes=[], fliplr=False):
    """
    Given a connectivity matrix and a (x,y,z) centers file for each region, plot the 3D network
    """
    matrix = core.file_reader(connectmat_file)
    nodes = core.file_reader(centers_file)
    if names_file:
        names = core.file_reader(names_file,1)
    num_nodes = len(nodes)
    edge_thresh_pct = threshold_pct / 100.0
    matrix_flat = np.array(matrix).flatten()
    edge_thresh = np.sort(matrix_flat)[len(matrix_flat)-int(len(matrix_flat)*edge_thresh_pct)]
    
    matrix = core.file_reader(connectmat_file)
    ma = np.array(matrix)

    thresh = scipy.stats.scoreatpercentile(ma.ravel(),100-threshold_pct)
    ma_thresh = ma*(ma > thresh)
    
    if highlight_nodes:
        nr = ma.shape[0]
        subset_mat = np.zeros((nr, nr))
        for i in highlight_nodes:
            subset_mat[i,:] = 1
            subset_mat[:,i] = 1
        ma_thresh = ma_thresh * subset_mat
        
    if fliplr:
        new_nodes = []
        for node in nodes:
            new_nodes.append([45-node[0],node[1],node[2]]) # HACK
        nodes = new_nodes
    
    mlab.figure(bgcolor=(1, 1, 1), size=(400, 400))
    for count,(x,y,z) in enumerate(nodes):
        if node_indiv_colors:
            mlab.points3d(x,y,z, color=colors[node_indiv_colors[count]], scale_factor=node_scale_factor, resolution=resolution)
        else:
            mlab.points3d(x,y,z, color=(0,1,0), scale_factor=node_scale_factor, resolution=resolution)
        if names_file:
            width = .025*name_scale_factor*len(names[count])
            print width
            print names[count]
            mlab.text(x, y,names[count], z=z,width=.025*len(names[count]),color=(0,0,0))
    for i in range(num_nodes-1):    
        x0,y0,z0 = nodes[i]
        for j in range(i+1, num_nodes):
            #if matrix[i][j] > edge_thresh:
            if ma_thresh[i][j] > edge_thresh:
                x1,y1,z1 = nodes[j]
                if weight_edges:
                    mlab.plot3d([x0,x1], [y0,y1], [z0,z1],
                            tube_radius=matrix[i][j]/matrix_flat.max(),
                            color=(1,1,1))
                else:
                    mlab.plot3d([x0,x1], [y0,y1], [z0,z1],
                            tube_radius=edge_radius,
                            color=(1,1,1))

def plot_matrix_metric(connectmat_file,centers_file,threshold_pct,grp_metrics=None,node_metric='bc',
                       weight_edges=0,node_scale_factor=2,edge_radius=.5,resolution=8,name_scale_factor=1,names_file=0,
                       red_nodes=None):
    """
    Given a connectivity matrix and a (x,y,z) centers file for each region, plot the 3D network
    """
    matrix=core.file_reader(connectmat_file)
    nodes=core.file_reader(centers_file)
    if names_file:
        names = core.file_reader(names_file,1)
    num_nodes = len(nodes)
    edge_thresh_pct = threshold_pct / 100.0
    matrix_flat=np.array(matrix).flatten()
    edge_thresh=np.sort(matrix_flat)[len(matrix_flat)-int(len(matrix_flat)*edge_thresh_pct)]
    
    if grp_metrics: # regional metrics caclulated elsewhere, loaded in
        node_colors = {}     # define colors for each metric
        node_colors['s'] = (1,  0.733,  0)
        node_colors['cc'] = (0.53, 0.81, 0.98)
        node_colors['bc'] = (0.5,  1,  0)
        node_colors['eloc'] = (1,  0 ,  1)
        node_colors['ereg'] = (1,  1,  0)
        
        node_metrics={}
        metrics = np.array(core.file_reader(grp_metrics))
        cols = np.shape(metrics)[1]
        for i in range(cols):
            colmean = np.mean(metrics[:,i])
            colscale = 2 / colmean
            metrics[:,i] = metrics[:,i] * colscale # make node mean size 2
        node_metrics['s'] = metrics[:,0] # strength
        node_metrics['cc'] = metrics[:,1] # clustering coefficient
        node_metrics['bc'] = metrics[:,2] # betweenness centrality
        node_metrics['eloc'] = metrics[:,3] # local efficiency
        node_metrics['ereg'] = metrics[:,4] # regional efficiency
    
    mlab.figure(bgcolor=(1, 1, 1), size=(800, 800))
    for count,(x,y,z) in enumerate(nodes):
        if grp_metrics:
            mlab.points3d(x,y,z, color=node_colors[node_metric],
                          scale_factor=node_metrics[node_metric][count], resolution=resolution)
        else:
            mlab.points3d(x,y,z, color=(0,1,0), scale_factor=node_scale_factor, resolution=resolution)
        if names_file:
            mlab.text(x, y,names[count], z=z,width=.02*name_scale_factor*len(names[count]),color=(0,0,0))
    
    for i in range(num_nodes-1):    
        x0,y0,z0=nodes[i]
        for j in range(i+1, num_nodes):
            if matrix[i][j] > edge_thresh:
                x1,y1,z1=nodes[j]
                if weight_edges:
                    mlab.plot3d([x0,x1], [y0,y1], [z0,z1],
                            tube_radius=matrix[i][j]/matrix_flat.max(),
                            color=(1,1,1))
                else:
                    mlab.plot3d([x0,x1], [y0,y1], [z0,z1],
                            tube_radius=edge_radius,
                            color=(1,1,1))

def plot_matrix_stats(connectmat_file, centers_file, threshold_pct, stats_file,
                      weight_edges=0, node_scale_factor=2, edge_radius=.5, resolution=8,
                      name_scale_factor=1, names_file=0):
    """
    Given a connectivity matrix and a (x,y,z) centers file for each region, plot the 3D network;
    stats file contains one column for nodes, and matrix for edges, with 1's for regions with
    significant difference and 0's for regions without
    """
    matrix=core.file_reader(connectmat_file)
    nodes=core.file_reader(centers_file)
    if names_file:
        fin = open(names_file)
        names = []
        for line in fin:
            vals = line.rstrip()
            names.append(vals)
        fin.close()
    fin = open(stats_file)
    stats_list = []
    for line in fin:
        pos = line.rstrip().split()
        stats_list.append(map(int,map(float, pos)))
    fin.close()
    stats=np.array(stats_list)
    node_stats = stats[:,0]
    edge_stats= stats[:,1:]    
    num_nodes=len(nodes)
    edge_thresh_pct=(float(threshold_pct)/100)
    matrix_flat=np.array(matrix).flatten()
    edge_thresh=np.sort(matrix_flat)[len(matrix_flat)-int(len(matrix_flat)*edge_thresh_pct)]
    mlab.figure(bgcolor=(1, 1, 1), size=(400, 400))
    for count,(x,y,z) in enumerate(nodes):
        if node_stats[count]==1:
            mlab.points3d(x,y,z, color=(1,0,0), scale_factor=node_scale_factor,resolution=resolution)
            if names_file:
                mlab.text(x, y,names[count], z=z,width=.025*name_scale_factor,color=(0,0,0))
        elif node_stats[count]==2:
            mlab.points3d(x,y,z, color=(0,0,1), scale_factor=node_scale_factor)
            if names_file:
                mlab.text(x, y,names[count], z=z,width=.025*name_scale_factor,color=(0,0,0))
        else:
            mlab.points3d(x,y,z, color=(0,1,0), scale_factor=node_scale_factor)
    for i in range(num_nodes-1):
        x0,y0,z0=nodes[i]
        for j in range(i+1, num_nodes):
            if edge_stats[i][j] == 1:
                    x1,y1,z1=nodes[j]
                    if weight_edges:
                        mlab.plot3d([x0,x1], [y0,y1], [z0,z1],
                                tube_radius=matrix[i][j]/matrix_flat.max(),
                                color=(1,0,0))
                    else:
                        mlab.plot3d( [x0,x1], [y0,y1], [z0,z1],
                            tube_radius=edge_radius,
                            color=(1,0,0) )
            elif matrix[i][j] > edge_thresh:
                    x1,y1,z1=nodes[j]
                    if weight_edges:
                        mlab.plot3d([x0,x1], [y0,y1], [z0,z1],
                                tube_radius=matrix[i][j]/matrix_flat.max(),
                                color=(1,1,1))
                    else:
                        mlab.plot3d([x0,x1], [y0,y1], [z0,z1],
                            tube_radius=edge_radius,
                            color=(1,1,1))
                        
def plot_matrix_stats_features(connectmat_file, centers_file, threshold_pct, stats_file,
                      weight_edges=0, node_scale_factor=2, edge_radius=.5, resolution=8,
                      name_scale_factor=1, names_file=0, num_stats=5):
    """
    Given a connectivity matrix and a (x,y,z) centers file for each region, plot the 3D network;
    stats file contains num_stats columns for nodes, and matrix for edges, with 1's for regions with
    significant difference and 0's for regions without
    """
    matrix = core.file_reader(connectmat_file)
    nodes = core.file_reader(centers_file)
    if names_file:
        fin = open(names_file)
        names = []
        for line in fin:
            vals = line.rstrip()
            names.append(vals)
        fin.close()
    fin = open(stats_file)
    stats_list = []
    for line in fin:
        pos = line.rstrip().split()
        stats_list.append(map(int, map(float, pos)))
    fin.close()
    stats = np.array(stats_list)
    node_stats = stats[:, 0:num_stats]
    edge_stats = stats[:, num_stats:]
    node_colors = {}     # define colors for each metric
    node_colors['s'] = (1, 0.733, 0)
    node_colors['cc'] = (0.53, 0.81, 0.98)
    node_colors['bc'] = (0.5, 1, 0)
    node_colors['part_coef'] = (1, 0 , 1)
    node_colors['ereg'] = (1, 1, 0)
    node_colors_list = [(1, 0.733, 0), (0.53, 0.81, 0.98), (0.5, 1, 0), (1, 1, 0), (1, 0, 1)]
    
    num_nodes=len(nodes)
    edge_thresh_pct=(float(threshold_pct)/100)
    matrix = np.array(matrix)
    # functional connectivity minimum shift
    if np.min(matrix) < 0:
        matrix = matrix - np.min(matrix)
    matrix_flat=np.array(matrix).flatten()
    edge_thresh=np.sort(matrix_flat)[len(matrix_flat)-int(len(matrix_flat)*edge_thresh_pct)]
    mlab.figure(bgcolor=(1, 1, 1), size=(400, 400))
    for count, (x,y,z) in enumerate(nodes):
        if np.sum(node_stats[count,:]) > 1: # if more than one measure is significant, color node red
            mlab.points3d(x,y,z, color=(1,0,0), scale_factor=4*node_scale_factor,resolution=resolution)
            if names_file:
                mlab.text(x, y,names[count], z=z, width=.025*name_scale_factor, color=(0,0,0))
        elif np.sum(node_stats[count,:]) == 1:
            metric_num = int(np.nonzero(node_stats[count,:]==1)[0])
            mlab.points3d(x,y,z, color=node_colors_list[metric_num], scale_factor=3*node_scale_factor,resolution=resolution)
            if names_file:
                mlab.text(x, y,names[count], z=z,width=.025*name_scale_factor,color=(0,0,0))
        else:
            mlab.points3d(x,y,z, color=(1,1,1), scale_factor=node_scale_factor)
    for i in range(num_nodes-1):
        x0,y0,z0=nodes[i]
        for j in range(i+1, num_nodes):
            if edge_stats[i][j] == 1:
                    x1,y1,z1=nodes[j]
                    if weight_edges: # Using sqrt on edges!!
                        mlab.plot3d([x0,x1], [y0,y1], [z0,z1],
                                tube_radius = np.sqrt((matrix[i][j]/matrix_flat.max())) * edge_radius,
                                color=(1,0,0))
                    else:
                        mlab.plot3d( [x0,x1], [y0,y1], [z0,z1],
                            tube_radius=edge_radius,
                            color=(1,0,0) )
            elif matrix[i][j] > edge_thresh:
                    x1,y1,z1=nodes[j]
                    if weight_edges: # Using sqrt on edges!!
                        mlab.plot3d([x0,x1], [y0,y1], [z0,z1],
                                tube_radius = np.sqrt((matrix[i][j]/matrix_flat.max())) * edge_radius,
                                color=(1,1,1))
                    else:
                        mlab.plot3d([x0,x1], [y0,y1], [z0,z1],
                            tube_radius=edge_radius,
                            color=(1,1,1))
                    
def plot_matrix_path(connectmat_file,centers_file,paths_file,path_num=0,threshold_pct=5,weight_edges=False,
                     node_scale_factor=2,edge_radius=.5,resolution=8,name_scale_factor=1,names_file=0):
    """
    Given a connectivity matrix and a (x,y,z) centers file for each region, plot the 3D network;
    paths file contains columns listing nodes contained in path
    """
    matrix=core.file_reader(connectmat_file)
    nodes=core.file_reader(centers_file)
    paths=zip(*core.file_reader(paths_file))
    path=paths[path_num]
    path_pairs=zip(path[0:len(path)-1],path[1:])
    print path_pairs
    if names_file:
        names=core.file_reader(names_file)
    num_nodes=len(nodes)
    edge_thresh_pct=(float(threshold_pct)/100)
    matrix_flat=np.array(matrix).flatten()
    edge_thresh=np.sort(matrix_flat)[len(matrix_flat)-int(len(matrix_flat)*edge_thresh_pct)]
    mlab.figure(bgcolor=(1, 1, 1), size=(400, 400))
    for count,(x,y,z) in enumerate(nodes):
        mlab.points3d(x,y,z, color=(0,1,0), scale_factor=node_scale_factor, resolution=resolution)
        if names_file:
            width=.025*name_scale_factor*len(names[count])
            mlab.text(x, y,names[count], z=z,width=.025*name_scale_factor,color=(0,0,0))
    for i in range(num_nodes-1):    
        x0,y0,z0=nodes[i]
        for j in range(i+1, num_nodes): 
            if matrix[i][j] > edge_thresh:
                x1,y1,z1=nodes[j]
                if weight_edges:
                    mlab.plot3d([x0,x1], [y0,y1], [z0,z1],
                            tube_radius=matrix[i][j]/matrix_flat.max(),
                            color=(1,1,1))
                else:
                    mlab.plot3d([x0,x1], [y0,y1], [z0,z1],
                            tube_radius=edge_radius,
                            color=(1,1,1))
    for n1,n2 in path_pairs:
        n1=int(n1)
        n2=int(n2)
        x0,y0,z0=nodes[n1]
        x1,y1,z1=nodes[n2]
        mlab.plot3d( [x0,x1], [y0,y1], [z0,z1],
                    tube_radius=1,
                    color=(0,0,1))

def plot_volume(nifti_file,v_color=(.98,.63,.48),v_opacity=.1, fliplr=False, newfig=False):
    """
    Render a volume from a .nii file
    Use fliplr option if scan has radiological orientation
    """
    import nibabel as nib
    if newfig:
        mlab.figure(bgcolor=(1, 1, 1), size=(400, 400))
    input = nib.load(nifti_file)
    input_d = input.get_data()
    d_shape = input_d.shape
    if fliplr:
        input_d = input_d[range(d_shape[0]-1,-1,-1), :, :]
    mlab.contour3d(input_d, color=v_color, opacity=v_opacity) # good natural color is (.98,.63,.48)

def rescale(in_array,new_min,new_max):
    rescale_range = new_max - new_min
    out_array = in_array - min(in_array)
    out_array = rescale_range * (out_array / max(out_array))
    out_array = out_array + new_min
    return out_array

def plot_matrix_2d(connectmat_file,centers_file,names_file=None,grp_metrics=None,grp_stats=None,grp_stats_p=.01,
                   node_metric='bc',threshold_pct=0,binarize=False,weight_edges=False,edge_interval_pct=10,
                   rescale_metric=False, connectmat_file2=None, orientation='Axial',node_subset=[],
                   node_indiv_colors=[], highlight_nodes=[]):
    """
    Given connectivity matrix and (x,y) centers, use networkx and matplotlib
    to make 2d network plot
    Node metric options are 'ones' (all radii equal to 1), 's' (strength), 'cc' (clustering coefficnet),
    'bc' (betweenness centrality) and if they are loaded in grp_metrics,
    'eloc' (local efficiency) and 'ereg' (regional efficiency)
    """
    m = core.file_reader(connectmat_file)
    ma = np.array(m)
    if threshold_pct:
        thresh = scipy.stats.scoreatpercentile(ma.ravel(),100-threshold_pct)
        ma_thresh = ma*(ma > thresh)
    else:
        ma_thresh = ma
    ma_bin = 1*(ma_thresh != 0)
    if binarize:
        ma_thresh = 1*(ma_thresh != 0)
    G = nx.Graph(ma_thresh)
    centers = core.file_reader(centers_file)
    
    if connectmat_file2: # plot graph comparison
        m2 = core.file_reader(connectmat_file2)
        ma2 = np.array(m2)
        if threshold_pct:
            thresh = scipy.stats.scoreatpercentile(ma2.ravel(),100-threshold_pct)
            ma2_thresh = ma2*(ma2 > thresh)
        else:
            ma2_thresh = ma2
        ma2_bin = 1*(ma2_thresh != 0)
        if binarize:
            ma2_thresh = 1*(ma2_thresh != 0)

        common = (ma_bin * ma2_bin) * ((ma_thresh * ma_thresh) / 2)
        ma_only = 1*(ma_bin-ma2_bin>0) * ma_thresh
        ma2_only = 1*(ma2_bin-ma_bin>0) * ma2_thresh
        if node_subset:
            nr = ma.shape[0]
            subset_mat = np.zeros((nr, nr))
            subset_vec = np.zeros(nr)
            for i in node_subset:
                for j in node_subset:
                    if i != j:
                        subset_mat[i,j] = 1
                        subset_mat[j,i] = 1
                        subset_vec[i] = 1
            out = common * subset_mat
            G1 = nx.Graph(common * subset_mat)
            G2 = nx.Graph(ma_only * subset_mat) 
            G3 = nx.Graph(ma2_only * subset_mat)
        else:
            G1 = nx.Graph(common)
            G2 = nx.Graph(ma_only)
            G3 = nx.Graph(ma2_only)
            
    if highlight_nodes:
        nr = ma.shape[0]
        subset_mat = np.zeros((nr, nr))
        for i in highlight_nodes:
            subset_mat[i,:] = 1
            subset_mat[:,i] = 1
        G = nx.Graph(ma_thresh * subset_mat)

    if names_file:
        names = core.file_reader(names_file,1)
        names_dict={}
        if node_subset:
            for i in node_subset:
                names_dict[i] = names[i]
        else:
            for i in range(len(names)):
                names_dict[i] = names[i]
    else:
        names_dict={}
        for i in range(ma.shape[0]):
            names_dict[i] = ''
    node_colors = {} # define colors for each metric
    node_colors['ones'] = 'gray'
    node_colors['s'] = 'orange'
    node_colors['cc'] = 'aqua'
    node_colors['bc'] = 'chartreuse'
    node_colors['eloc'] = 'magenta'
    node_colors['ereg'] = 'yellow'
    node_metrics={}
    cols = np.shape(ma)[1]
    node_metrics['ones'] = np.ones(cols)*300
    if grp_metrics: # regional metrics caclulated elsewhere, loaded in
        metrics = np.array(core.file_reader(grp_metrics))
        cols = np.shape(metrics)[1]
        for i in range(cols):
            if rescale_metric: # scale metrics between 30 and 3000
                metrics[:,i] = rescale(metrics[:,i],200,1000)
            else: # make mean metric 300 # change to abs if negative values are included
                colmean = np.mean(metrics[:,i])
                colscale = 300 / colmean
                metrics[:,i] = metrics[:,i] * colscale
        node_metrics['s'] = metrics[:,0] # ereg
        node_metrics['cc'] = metrics[:,1] # ecc
    else: # otherwise, calculate them locally
        bc = nx.betweenness_centrality(G,weight=True)
        bcs = np.array([bc[x] for x in bc])
        bcscale = 300 / np.mean(bcs)
        bcs = bcs * bcscale
        node_metrics['bc'] = bcs
        
        deg = nx.degree(G)
        degs = np.array([deg[x] for x in deg])
        degscale = 300 / np.mean(degs)
        degs = degs * degscale
        node_metrics['s'] = degs
        
        cc = nx.clustering(G, weight=True)
        ccs = []
        ccs = np.array([cc[x] for x in cc])
        
        #cc_dict = nx.clustering(G, weighted=True)
        #cc = np.array(cc_dict[0].values())
        #cc_weights = np.array(cc_dict[1].values())
        #ccs = cc * cc_weights # multiply ccs by weights
        
        ccscale = 300 / np.mean(ccs)
        ccs = ccs * ccscale
        node_metrics['cc'] = ccs
    if grp_stats: # p-values of differences in regional metrics between groups
        node_stats={}
        stats = np.array(core.file_reader(grp_stats))
        node_stats['s'] = stats[:,0] # strength
        node_stats['cc'] = stats[:,1] # clustering coefficient
        #node_stats['bc'] = stats[:,2] # betweenness centrality
        #node_stats['eloc'] = stats[:,3] # local efficiency
        #node_stats['ereg'] = stats[:,4] # regional efficiency
    centersa = np.array(centers)
    ############
    if orientation == 'Sagittal':
        centersxy = centersa[:,1:]
    elif orientation == 'Coronal':
        centersxy = np.column_stack((centersa[:,0],centersa[:,2]))
    else:
        #centersxy = centersa[:,0:2]
        centersxy = centersa[:,0:2]*[-1,1] # comment in [-1,1] to REVERSE X-AXIS; flips labels accordingly
        
    basesize = 6
    xr = abs(min(centersxy[:,0])) + abs(max(centersxy[:,0]))
    yr = abs(min(centersxy[:,1])) + abs(max(centersxy[:,1]))

    xy_ratio = max(xr,yr)/min(xr,yr)
    if xr > yr:
        xy_size = (basesize*xy_ratio, basesize)
    else:
        xy_size = (basesize, basesize*xy_ratio)
    
    plt.figure(figsize=xy_size)

    if grp_stats:
        # create two graphs of nodes, significant and non-significant differences
        Gnonsig = nx.Graph() # add nodes with metric value > p-val
        Gnonsig_nodes = np.nonzero(node_stats[node_metric] >= grp_stats_p)[0]
        Gnonsig.add_nodes_from(Gnonsig_nodes)
        Gsig = nx.Graph() # add nodes with metric value < p-val
        Gsig_nodes = np.nonzero(node_stats[node_metric] < grp_stats_p)[0]
        Gsig.add_nodes_from(Gsig_nodes)
        node_nonsigcolors = {}     # define light colors for nonsignificant nodes
        node_nonsigcolors['s'] = 'orange' #(0.93333333,  0.63529412,  0.67843137)
        node_nonsigcolors['cc'] = 'aqua' #(0.65490196,  0.75686275,  0.9254902) 
        node_nonsigcolors['bc'] = 'chartreuse' #(0.68627451,  0.93333333,  0.6627451)
        node_nonsigcolors['eloc'] = 'magenta' #(0.93333333,  0.6627451 ,  0.92941176)
        node_nonsigcolors['ereg'] = 'yellow' #(0.93333333,  0.92941176,  0.6627451)
        node_sigcolors = {}     # define primary colors for significant nodes
        node_sigcolors['s'] = 'red'#'red'
        node_sigcolors['cc'] = 'red'#'aqua'
        node_sigcolors['bc'] = 'red'#'chartreuse'
        node_sigcolors['eloc'] = 'red'#'magenta'
        node_sigcolors['ereg'] = 'red'#'yellow'
        nx.draw_networkx_nodes(Gnonsig,centersxy,
                               node_size = node_metrics[node_metric][Gnonsig.nodes()],
                               alpha = 1,
                               node_color = node_nonsigcolors[node_metric])
        nonsiglabels = dict([[n,names_dict[n]] for n in Gnonsig_nodes])
        # this draws all labels in dictionary, not just those from Gnonsig
        nx.draw_networkx_labels(Gnonsig,centersxy,labels=nonsiglabels,font_size=8)
        nx.draw_networkx_nodes(Gsig,centersxy,
                               node_size = node_metrics[node_metric][Gsig.nodes()],
                               alpha = 1,
                               node_color = node_sigcolors[node_metric])
        siglabels = dict([[n,names_dict[n]] for n in Gsig_nodes])
        nx.draw_networkx_labels(Gsig,centersxy,
                                labels=siglabels,font_size=12,font_weight='bold')
        plt.autoscale(tight=True)
    elif node_indiv_colors:
        nx.draw_networkx_nodes(G,centersxy,node_size = node_metrics[node_metric],node_color=node_indiv_colors)
        plt.autoscale(tight=True)
        if names_file:
            nx.draw_networkx_labels(G,centersxy,labels=names_dict,font_size=10)        
    else:
        nx.draw_networkx_nodes(G,centersxy,node_size = node_metrics[node_metric],node_color=node_colors[node_metric])
        plt.autoscale(tight=True)
        if names_file:
            nx.draw_networkx_labels(G,centersxy,labels=names_dict,font_size=10)
    if weight_edges:
        edges = []
        nonzero_edges = ma_thresh[np.nonzero(ma_thresh)] # all nonzero edges
        percentiles = [core.my_scoreatpercentile(nonzero_edges, 100-x) for x in range(0,101,edge_interval_pct)]
        for i in range(len(percentiles)-1):
            alpha_val = .1 + (i / 20.0) # edges in first percentile have alpha=0
            thresh_low = percentiles[i]
            thresh_high = percentiles[i+1]
            edges.append([(u,v) for (u,v,d) in G.edges(data=True) if thresh_low <= d['weight'] <= thresh_high])
            nx.draw_networkx_edges(G,centersxy,edgelist=edges[i],width=float(i/2),alpha=alpha_val,edge_color='k')


        plt.autoscale(tight=True)
    else:
        nx.draw_networkx_edges(G,centersxy,width=1,alpha=.5,edge_color='k')
        plt.autoscale(tight=True)
    if connectmat_file2:
        plt.close()
        plt.figure(figsize=xy_size)
        if node_indiv_colors:
            nx.draw_networkx_nodes(G,centersxy,node_size = node_metrics[node_metric]*subset_vec,node_color=node_indiv_colors)
        else:
            nx.draw_networkx_nodes(G,centersxy,node_size=node_metrics[node_metric]*subset_vec,node_color=node_colors[node_metric])
        if names_file:
            nx.draw_networkx_labels(G,centersxy,labels=names_dict,font_size=10)
        nx.draw_networkx_edges(G1,centersxy,width=1,alpha=.3,edge_color='k')
        nx.draw_networkx_edges(G2,centersxy,width=1,alpha=1,edge_color='blue')
        nx.draw_networkx_edges(G3,centersxy,width=1,alpha=1,edge_color='red')
        plt.autoscale(tight=True)
    plt.show()
    
def plot_spring(connectmat_file,comm_index_file,node_indiv_colors,
                threshold_pct=2,binarize=False,weight_edges=False,names_file=None):
    """
    Given connectivity matrix,
    a community index file (integer on each line specifying which module that node belongs to),
    and python list of strings specifying color for each node,
    use networkx and matplotlib to generate 2d spring-embedded plot
    """
    alpha = .5
    edge_interval_pct = 10
    m = core.file_reader(connectmat_file)
    ma = np.array(m)
    if threshold_pct:
        thresh = scipy.stats.scoreatpercentile(ma.ravel(),100-threshold_pct)
        ma_thresh = ma*(ma > thresh)
    else:
        ma_thresh = ma
    ma_bin = 1*(ma_thresh != 0)
    if binarize:
        ma_thresh = 1*(ma_thresh != 0)
    cmat_thresh = ma_thresh
    G = nx.Graph(ma_thresh)
    
    partition_list = core.file_reader(comm_index_file)
    partition = {}
    for count,i in enumerate(partition_list):
        partition[count] = i[0]
    
    if names_file:
        names = core.file_reader(names_file,1)
        names_dict={}
        for i in range(len(names)):
            names_dict[i] = names[i]
    else:
        names_dict={}
        for i in range(ma.shape[0]):
            names_dict[i] = ''
    
    size = float(len(set(partition.values())))
    pos = nx.spring_layout(G, fixed=[0])

    #module_colors = [0]*len(names_dict)
    #count = 0.
    #for com in set(partition.values()) :
    #    count = count + 1.
    #    list_nodes = [nodes for nodes in partition.keys()
    #                                if partition[nodes] == com]
    #rgb = matplotlib.cm.jet(norm(fracs[count-1]))[0:3]
    #rgb_255 = tuple([int(a*255) for a in rgb])
    #hex = '#%02x%02x%02x' % tuple(rgb_255)
    #for node in list_nodes:
    #    module_colors[node] = hex

    module_colors = [colors[node] for node in node_indiv_colors]
    count = 0.
    for com in set(partition.values()) :
        count = count + 1.
        list_nodes = [nodes for nodes in partition.keys() if partition[nodes] == com]
        cur_mod_colors = [module_colors[node] for node in list_nodes]
        nx.draw_networkx_nodes(G, pos, list_nodes, node_size = 200,
                               node_color = cur_mod_colors)
    
    if weight_edges:
        edges = []
        nonzero_edges = cmat_thresh[np.nonzero(cmat_thresh)] # all nonzero edges
        percentiles = [core.my_scoreatpercentile(nonzero_edges, 100-x) for x in range(0,101,edge_interval_pct)]
        for i in range(len(percentiles)-1):
            alpha_val = .1 + (i / 20.0) # edges in first percentile have alpha=0
            thresh_low = percentiles[i]
            thresh_high = percentiles[i+1]
            edges.append([(u,v) for (u,v,d) in G.edges(data=True) if thresh_low <= d['weight'] <= thresh_high])
            nx.draw_networkx_edges(G,pos,edgelist=edges[i],width=i/1.9,alpha=alpha_val,edge_color='k')
    else:
        nx.draw_networkx_edges(G, pos, width=1, alpha=alpha)
        
    if names_file:
        nx.draw_networkx_labels(G, pos, labels=names_dict, font_size=10)
    plt.autoscale(tight=True)
    
def plot_tracks(trk_file):
    """
    Plot streamlines from a DSI Studio .txt tracks file
    """
    trks = core.file_reader(trk_file)
    ta = np.array(trks)
    for t in ta:
        tl = len(t)
        trs = np.reshape(t, (tl/3,3))
        mlab.plot3d(trs[:,0], trs[:,1], trs[:,2])
        
def animation(delay=50, continuous=False, degree_step=2, save_movie=False):
    # IN PROGRESS
    from mayavi import mlab
    @mlab.animate(delay=delay)
    def anim():
        f = mlab.gcf()
        for count, i in enumerate(range(2,361,2)):
        #while 1:
            f.scene.camera.azimuth(degree_step)
            f.scene.render()
            mlab.savefig('/Users/jessebrown/Desktop/mayavi_figs/r_hipp_network%03d.png' %count)
            yield
    
    a = anim() # Starts the animation.
    if save_movie:
        pass
        #ffmpeg -y -i "r_hipp_network%03d.png" -b 5000k movie.mp4 # need to system call this